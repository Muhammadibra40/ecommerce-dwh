from time import time
from dotenv import load_dotenv
import pandas as pd
import re
import pyodbc
import os



class ECommerceETL:
    def __init__(self):
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('servername')};"
            f"DATABASE={os.getenv('db')};"
            f"Trusted_Connection=yes;"
        )


    def extract_from_csv(self, file_path):
        try:
            data = pd.read_csv(
                file_path,
                encoding='ISO-8859-1',
                dtype={
                    'InvoiceNo': 'str',
                    'StockCode': 'str',
                    'Description': 'str',
                    'CustomerID': 'str',
                    'Country': 'str'
                },
                parse_dates=['InvoiceDate']
            )

            initial_count = len(data)

            df = data[data['CustomerID'].notna()].copy()
  
            print(f"Total Extracted: {initial_count} rows, filtered out: {initial_count - len(df)} invalid rows, Final extracted records: {len(df)} valid rows")

            return df
        except Exception as e:
                print(f"Error: {str(e)}")
                return None
        

    def clean_data(self, df):
        df = df.copy()

        df.columns = [
            re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', col).lower()
            for col in df.columns
        ]
        
        initial_count = len(df)

        df.loc[:, 'quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype('int32')
        df.loc[:, 'unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0.0)

        df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)]

        df.loc[:, 'description'] = df['description'].str.slice(0, 255)
        df.loc[:, 'stock_code'] = df['stock_code'].str.strip().str.upper()

        print(f"Total Extracted: {initial_count} rows, filtered out: {initial_count - len(df)} invalid rows, Final clean records: {len(df)} valid rows")

        return df

    def load_to_sql(self, df, table_name, schema="dbo", batch_size=1000):
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            full_table_name = f"[{schema}].[{table_name}]"
            batch_no = 1

            insert_sql = f"""
            INSERT INTO {full_table_name} (
                invoice_no, stock_code, description, 
                quantity, invoice_date, unit_price, 
                customer_id, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            anomalies = (
                df.groupby(['invoice_no', 'stock_code', 'description', 'quantity', 'invoice_date'])
                .filter(lambda x: x['unit_price'].nunique() > 1)
                .copy()
            )
            anomalies['price_issue'] = 'inconsistent prices'

            zero_or_negative_prices = df[round(df["unit_price"], 2) <= 0].copy()
            zero_or_negative_prices['price_issue'] = 'zero after rounding'

            pricing_issues = pd.concat([anomalies, zero_or_negative_prices]).drop_duplicates()

            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


            logs_path = os.path.join(root_dir, 'logs', 'pricing_anomalies.csv')

            pricing_issues.to_csv(logs_path, index=False)

            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]

                
                data = [
                    (
                        str(row.invoice_no),
                        str(row.stock_code),
                        str(row.description),
                        int(row.quantity),
                        row.invoice_date.to_pydatetime() if hasattr(row.invoice_date, 'to_pydatetime') else row.invoice_date,
                        float(row.unit_price),
                        str(row.customer_id),
                        str(row.country)
                    )
                    for row in batch.itertuples(index=False)
                ]
                cursor.executemany(insert_sql, data)
                conn.commit()
                print(f"Batch load no.{batch_no} is complete")
                batch_no += 1

            print(f"Successfully loaded {len(df)} rows into {full_table_name}")
            return True
        except Exception as e:
                print(f"SQL Error: {str(e)}")
                return False
        
    def validate_sql_load(self, table_name, schema="dbo"):
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM [{schema}].[{table_name}] 
            WHERE quantity > 0 AND unit_price <= 0
        """)
        count = cursor.fetchone()[0]
        print(f"Post-load validation: {count} suspicious rows found.")

        

    def execute_sql_procedure(self, procedure_name):
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            cursor.execute(f"EXEC {procedure_name}")
            
            rows_affected = None
            while cursor.nextset():
                result = cursor.fetchone()
                if result:
                    rows_affected = result[0]
            
            conn.commit()
            print(f"Rows affected: {rows_affected}")
            cursor.close()
            conn.close()
            return rows_affected

        except Exception as e:
                print(f"Procedure Error: {str(e)}")
                return None
        


    def populate_dimensions(self):
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Customers dimension
            cursor.execute("""
            INSERT INTO dim_customer (customer_id, first_purchase_date, total_orders, total_spent)
            SELECT 
                customer_id,
                MIN(invoice_date),
                COUNT(DISTINCT invoice_no),
                SUM(quantity * unit_price)
            FROM cleaned_sales
            GROUP BY customer_id
            """)
            
            # Products dimension
            cursor.execute("""
            MERGE INTO dim_product AS target
            USING (
                SELECT 
                    stock_code,
                    MAX(description) AS description,
                    MAX(LEFT(description, CHARINDEX(' ', description + ' ') - 1)) AS category
                FROM cleaned_sales
                GROUP BY stock_code
            ) AS source
            ON (target.stock_code = source.stock_code)
            WHEN NOT MATCHED THEN
                INSERT (stock_code, description, category)
                VALUES (source.stock_code, source.description, source.category);
            """)
            
            # Time dimension
            cursor.execute("""
            INSERT INTO dim_time (time_key, full_date, day, month, year, 
                            quarter, day_of_week, day_name, month_name, is_weekend)
            SELECT DISTINCT
                CONVERT(INT, CONVERT(VARCHAR, CAST(invoice_date AS DATE), 112)),
                CAST(invoice_date AS DATE),
                DAY(invoice_date),
                MONTH(invoice_date),
                YEAR(invoice_date),
                DATEPART(QUARTER, invoice_date),
                DATEPART(WEEKDAY, invoice_date),
                DATENAME(WEEKDAY, invoice_date),
                DATENAME(MONTH, invoice_date),
                CASE WHEN DATEPART(WEEKDAY, invoice_date) IN (1, 7) THEN 1 ELSE 0 END
            FROM cleaned_sales
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_time 
                WHERE time_key = CONVERT(INT, CONVERT(VARCHAR, CAST(invoice_date AS DATE), 112))
            )
            """)
            conn.commit()
            return True
        except Exception as e:
                print(f"Size Error: {str(e)}")
                return False
        
    def populate_facts(self):
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO fact_sales (time_key, customer_key, product_key, 
                                quantity, unit_price, total_amount, country)
            SELECT 
                CONVERT(INT, CONVERT(VARCHAR, CAST(cs.invoice_date AS DATE), 112)),
                dc.customer_key,
                dp.product_key,
                cs.quantity,
                cs.unit_price,
                cs.quantity * cs.unit_price,
                cs.country
            FROM cleaned_sales cs
            JOIN dim_customer dc ON cs.customer_id = dc.customer_id
            JOIN dim_product dp ON cs.stock_code = dp.stock_code
            """)
            
            conn.commit()
            rows_inserted = cursor.rowcount
            print(f"Successfully loaded {rows_inserted} rows into fact_sales")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
                print(f"Fact Error: {str(e)}")
                return False
        
def run_full_pipeline(self, csv_path):
    start_time = time.time()
    
    # 1. Extract
    raw_data = self.extract_from_csv(csv_path)
    if raw_data is None: return False
    
    # 2. Clean
    cleaned_data = self.clean_data(raw_data)
    
    # 3. Load
    if not self.load_to_sql(cleaned_data, "RawSalesData"): return False
    
    # 4. Transform
    cleaned_rows = self.execute_sql_procedure("sp_CleanAndTransferData")
    if not cleaned_rows: return False
    
    # 5. Dimensions
    if not self.populate_dimensions(): return False
    
    # 6. Facts
    if not self.populate_facts(): return False
    
    duration = time.time() - start_time
    print(f"ETL completed. Duration: {duration:.2f} seconds")
    return True
    



# etl = ECommerceETL()
# # print(etl)

# # raw_data = etl.extract_from_csv(csv_path)
# # print("Raw Data: \n")
# # print(raw_data.head())

# # cleaned_data = etl.clean_data(raw_data)
# # print("Cleaned Data: \n")
# # print(cleaned_data.head())

# # etl.load_to_sql(cleaned_data, "raw_Sales")
# # etl.validate_sql_load("raw_Sales")

# # etl.execute_sql_procedure("sp_clean_and_transform_data")

# etl.populate_facts()