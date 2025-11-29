#import needed libraries
from sqlalchemy import create_engine
import pyodbc
import pandas as pd
import os
import re
from dotenv import load_dotenv
from datetime import datetime



load_dotenv() 


dir = os.getenv('dir')
username = os.getenv('username')
pwd = os.getenv('pwd')
servername = os.getenv('servername')
# port = os.getenv('port')
db = os.getenv('db')


def extract():
    try:
        directory = dir

        for filename in os.listdir(directory):

            file_wo_ext = os.path.splitext(filename)[0]
            file_wo_ext = re.sub(r"\s+", "_", file_wo_ext)

            if filename.endswith(".xlsx"):
                f = os.path.join(directory, filename)

                if os.path.isfile(f):
                    df = pd.read_excel(f)

                    print("Data extracted successfully")

                    load(df, file_wo_ext)
    except Exception as e:
        print("Data extract error: " + str(e))


def load(df, tbl):
    try:
        rows_imported = 0
        # connection_string = (
        #     f"mssql+pyodbc://{username}:{pwd}@{servername}/{db}"
        #     "?driver=ODBC+Driver+17+for+SQL+Server"
        # )
        connection_string = (
            f"mssql+pyodbc://@{servername}/{db}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )


        engine = create_engine(
            connection_string
        )
        


        # df_columns = df.columns
        # corrected_columns = []

        # for col in df_columns:
        #     corrected_columns.append(format_header(col))

        # df.columns = corrected_columns

        df.columns = [format_header(col) for col in df.columns]


        df['load_date'] = datetime.now()
        
        print(f'importing rows {rows_imported} to {rows_imported + len(df)}... ')

        df.to_sql(f"stg_{tbl}", engine, if_exists='replace', index=False)
        rows_imported += len(df)

        print("Data imported successfully")

    except Exception as e:
        print("Data load error: " + str(e))


def format_header(name):
    name = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name)
    return name.lower()


try:
    extract()
except Exception as e:
    print("Error while extracting data: " + str(e))