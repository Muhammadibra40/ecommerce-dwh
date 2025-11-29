from src.pipeline import ECommerceETL
from dotenv import load_dotenv
import os

load_dotenv()
csv_path = os.getenv('data_path')

if __name__ == "__main__":
    etl = ECommerceETL()
    success = etl.run_full_pipeline(csv_path)
    print("Success!" if success else "Error occurred!")