from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
from pathlib import Path

# ✅ Define the default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ✅ Define the DAG
dag = DAG(
    "ml_loan_training_pipeline",  # Name of the DAG
    default_args=default_args,
    schedule_interval="@daily",  # Runs every day
    catchup=False,
)

# ✅ Define a function to run the Python script
def run_ml_loan_train():
    """Function to run the ml_loan_train.py script in the virtual environment."""
    script_path = Path(__file__).resolve().parent.parent / "scripts/ml_loan_train.py"
    venv_python = Path(__file__).resolve().parent.parent / "venv/bin/python"

    # Run the script using the subprocess module
    subprocess.check_call([venv_python, script_path])

# ✅ Define Airflow Task
train_model_task = PythonOperator(
    task_id="train_ml_loan_model",
    python_callable=run_ml_loan_train,
    dag=dag,
)

# ✅ Run the ML training task
train_model_task
