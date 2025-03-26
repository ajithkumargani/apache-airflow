from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import psycopg2

# Database connection
DB_CONN = "dbname='weather' user='postgres' host='localhost' password='postgres'"

# OpenWeatherMap API (Replace with your API key)
API_KEY = " "
CITY = "New York"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Extract Weather Data
def fetch_weather():
    response = requests.get(URL)
    data = response.json()
    
    if response.status_code != 200 or "main" not in data:
        print(f"❌ API Error: {data}")
        df = pd.DataFrame(columns=["city", "date", "temperature", "humidity", "weather_description"])
    else:
        weather = {
            "city": CITY,
            "date": datetime.utcnow().date(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather_description": data["weather"][0]["description"]
        }
        df = pd.DataFrame([weather])
    
    # ✅ Ensure the file is always created
    df.to_csv("/tmp/weather_data.csv", index=False)
    print("✅ Weather data saved successfully.")


# Load Data into PostgreSQL
def load_weather_data():
    try:
        conn = psycopg2.connect(DB_CONN)
        cursor = conn.cursor()
        df = pd.read_csv("/tmp/weather_data.csv")

        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO public.weather_data (city, date, temperature, humidity, weather_description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (city, date) DO UPDATE 
                SET temperature = EXCLUDED.temperature, humidity = EXCLUDED.humidity, weather_description = EXCLUDED.weather_description;
                """,
                (row["city"], row["date"], row["temperature"], row["humidity"], row["weather_description"])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Weather data successfully loaded into the database.")

    except Exception as e:
        print(f"❌ Error loading weather data: {e}")

# DAG Configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "daily_weather_pipeline",
    default_args=default_args,
    schedule="0 6 * * *",  # Runs daily at 6 AM UTC
    catchup=False,
)

fetch_task = PythonOperator(task_id="fetch_weather", python_callable=fetch_weather, dag=dag)
load_task = PythonOperator(task_id="load_weather_data", python_callable=load_weather_data, dag=dag)

fetch_task >> load_task
