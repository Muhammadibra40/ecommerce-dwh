# E-Commerce Data Warehouse

## Overview  
**ecommerce-dwh** is a data warehousing project that consolidates and transforms e-commerce sales data into a structured, analytics-ready format.  
It provides a complete ETL pipeline: data ingestion → cleansing → transformation → dimensional modeling → analytics storage.

## Architecture

The project follows a **star schema** design with:
- **Fact Table**: `fact_sales` (transactional records)
- **Dimension Tables**: `dim_customers`, `dim_products`, `dim_time` (descriptive attributes)
- **Staging Table**: `raw_sales` (raw data before transformation)
- **Transformation Table**: `cleaned_sales` (cleansed data)

## Repository Structure  

```
ecommerce-dwh/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── pipeline.py              # Main ETL pipeline class
│   └── config.py                # Configuration & environment variables
├── data/
│   └── online_retail_data.csv   # Raw input data file
├── logs/
│   └── pricing_anomalies.csv    # Data quality issues detected during load
├── DB_DWH_DDL.sql               # Database schema & table definitions
├── E-Commerce Sales Cleansing.ipynb  # Data exploration & analysis notebook
├── EDA.sql                       # SQL exploratory data analysis queries
├── main.py                       # Entry point to run the ETL pipeline
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (⚠️ DO NOT COMMIT)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Prerequisites  

- **Python 3.8+**
- **SQL Server 2016+** (with ODBC Driver 17)
- **ODBC Driver 17 for SQL Server** installed
- Python packages (see `requirements.txt`)

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Muhammadibra40/ecommerce-dwh.git
cd ecommerce-dwh
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up database
```bash
# Execute the DDL script in SQL Server to create tables & schema
sqlcmd -S <your_server> -d <your_database> -i DB_DWH_DDL.sql
```

### 5. Configure environment variables
Create `.env` file in the root directory:
```env
DB_SERVER=your_sql_server_name
DB_NAME=ECommerceAnalytics
DATA_PATH=data/data.csv
```

 **Security**: Never commit `.env` with real credentials. Add to `.gitignore`.

### 6. Run the ETL pipeline
```bash
python main.py
```

## ETL Pipeline Flow

The pipeline executes the following steps:

1. **Extract** → Read CSV file into pandas DataFrame
2. **Clean** → Remove duplicates, nulls, invalid prices; standardize formats
3. **Load** → Insert raw data into `raw_sales` table with batch processing
4. **Transform** → Execute stored procedure `sp_CleanAndTransferData` to populate `cleaned_sales`
5. **Dimensions** → Populate `dim_customers`, `dim_products`, `dim_time` tables
6. **Facts** → Load `fact_sales` with aggregated metrics

**Output**: Success/failure status + execution time logged to console

## Key Features

✅ **Data Validation**: Detects pricing anomalies & invalid records (logged to `logs/pricing_anomalies.csv`)  
✅ **Batch Processing**: Loads data in 1000-row batches for performance  
✅ **Error Handling**: Comprehensive try-catch with rollback on failures  
✅ **Dimension Management**: MERGE operations to handle incremental updates  
✅ **Logging**: Pipeline progress & data quality metrics printed to console  

## Testing & Exploration

### Run exploratory analysis
```bash
# Use Jupyter to explore data before pipeline execution
jupyter notebook E-Commerce Sales Cleansing.ipynb
```

### Validate data warehouse
```bash
# Execute SQL queries to inspect results
sqlcmd -S <your_server> -d <your_database> -i EDA.sql
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Missing environment variables" | Check `.env` file exists with `DB_SERVER`, `DB_NAME`, `DATA_PATH` |
| "No results. Previous SQL was not a query" | Ensure stored procedure returns result set (check `sp_CleanAndTransferData`) |
| "Connection refused" | Verify SQL Server is running & ODBC Driver 17 is installed |
| Data not inserted | Check `logs/pricing_anomalies.csv` for rejected records |

## Possible Extensions

- ✨ Automated scheduling (Task Scheduler / Airflow / Azure Data Factory)
- 📈 BI dashboards (Power BI / Tableau integration)
- 🔍 Additional data sources (inventory, marketing, customer behavior)
- ✅ Unit tests & CI/CD pipeline
- 📊 Advanced analytics models (RFM, clustering, forecasting)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes & test end-to-end: `python main.py`
4. Commit with clear messages: `git commit -m "Add feature X"`
5. Submit a pull request

Ensure the pipeline runs successfully before submitting PRs.


## Contact

For questions, please contact me on:

- 📧 **Email**: [migibra678@gmail.com](mailto:migibra678@gmail.com)
- 💼 **LinkedIn**: [Muhammad Ibrahim](https://www.linkedin.com/in/muhammad-ibrahim-093293218/)
