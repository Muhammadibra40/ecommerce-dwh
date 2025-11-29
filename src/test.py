import pyodbc
import os 
from dotenv import load_dotenv
# print(pyodbc.drivers())

# root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# print(root_dir)

# logs_path = os.path.join(root_dir, 'logs', 'pricing_anomalies.csv')

# print(logs_path)


load_dotenv() 


dir = os.getenv('dir')
username = os.getenv('username')
pwd = os.getenv('pwd')
servername = os.getenv('servername')
# port = os.getenv('port')
db = os.getenv('db')

print(servername)
print(username)
print(pwd)
print(db)

import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-BGT4KHG;"
    "DATABASE=master;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Connected successfully via Python!")
except Exception as e:
    print("Error:", e)




