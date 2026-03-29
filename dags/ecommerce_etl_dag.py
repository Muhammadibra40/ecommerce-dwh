from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


from src.pipeline import ECommerceETL


default_args = {
    "owner": "muhammed",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")


def validate_input_data():
    """Check if data file exists"""
    if not DATA_PATH or not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
    print(f"Data found at {DATA_PATH}")


def run_etl_pipeline():
    """Run your existing ETL pipeline"""
    etl = ECommerceETL()
    success = etl.run_full_pipeline(DATA_PATH)

    if not success:
        raise Exception("ETL Pipeline failed")

    print("ETL completed successfully!")


def log_completion():
    print("Pipeline finished successfully 🎉")



with DAG(
    dag_id="ecommerce_etl_pipeline",
    default_args=default_args,
    description="E-commerce DWH ETL Pipeline",
    schedule_interval="@daily",   # You can change later
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "ecommerce", "dwh"],
) as dag:

    # Task 1: Validate Data
    validate_data = PythonOperator(
        task_id="validate_data",
        python_callable=validate_input_data,
    )

    # Task 2: Run ETL
    run_etl = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=run_etl_pipeline,
    )

    # Task 3: Completion log
    done = PythonOperator(
        task_id="done",
        python_callable=log_completion,
    )

    validate_data >> run_etl >> done