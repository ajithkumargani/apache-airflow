from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import psycopg2

# ✅ Corrected database connection
DB_CONN = "dbname='stocks' user='postgres' host='localhost' password='postgres'"

def extract_stock_data():
    stock = yf.Ticker("AAPL")
    data = stock.history(period="1d")
    data.reset_index(inplace=True)
    data.to_csv("/tmp/stock_data.csv", index=False)

def transform_stock_data():
    df = pd.read_csv("/tmp/stock_data.csv")
    
    # ✅ Ensure correct column naming to match PostgreSQL table
    df.rename(columns={"Date": "date", "Close": "close"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["close"] = df["close"].round(2)
    
    df.to_csv("/tmp/stock_data_transformed.csv", index=False)

def load_data_to_db():
    try:
        conn = psycopg2.connect(DB_CONN)
        cursor = conn.cursor()
        df = pd.read_csv("/tmp/stock_data_transformed.csv")

        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO public.stock_prices (date, close) 
                VALUES (%s, %s) 
                ON CONFLICT (date) 
                DO UPDATE SET close = EXCLUDED.close;
                """,
                (row["date"], row["close"])  # ✅ Ensure lowercase column names
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data successfully loaded into the database.")

    except Exception as e:
        print(f"❌ Error loading data to DB: {e}")

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ✅ Fix: Use `schedule` instead of `schedule_interval`
dag = DAG(
    "stock_etl_pipeline",
    default_args=default_args,
    schedule="0 0 * * *",  # Runs daily at midnight
    catchup=False,
)

# Task definitions
extract_task = PythonOperator(task_id="extract", python_callable=extract_stock_data, dag=dag)
transform_task = PythonOperator(task_id="transform", python_callable=transform_stock_data, dag=dag)
load_task = PythonOperator(task_id="load", python_callable=load_data_to_db, dag=dag)

# Task dependencies
extract_task >> transform_task >> load_task
