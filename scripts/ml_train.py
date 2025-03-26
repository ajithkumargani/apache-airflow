import pandas as pd
import joblib
import os
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ✅ Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(BASE_DIR, "data", "train_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODEL_DIR, "model.pkl")

# ✅ Ensure models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# ✅ Initialize MLflow
mlflow.set_experiment("ml_airflow_experiment")

def load_data():
    """Loads dataset."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"❌ Data file not found: {DATA_FILE}")
    return pd.read_csv(DATA_FILE)

def preprocess_data(df):
    """Splits dataset into training & testing sets."""
    X = df.drop(columns=["approved"])
    y = df["approved"]
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(X_train, X_test, y_train, y_test):
    """Trains and saves the model while logging with MLflow."""
    with mlflow.start_run():
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # ✅ Log parameters
        mlflow.log_param("n_estimators", 10)
        
        # ✅ Log model accuracy
        accuracy = accuracy_score(y_test, model.predict(X_test))
        mlflow.log_metric("accuracy", accuracy)
        
        # ✅ Save and log model
        joblib.dump(model, MODEL_FILE)
        mlflow.sklearn.log_model(model, "random_forest_model")
        
        print(f"✅ Model saved: {MODEL_FILE}")
        print(f"✅ Accuracy: {accuracy:.2%}")

def run_training():
    """Runs the full training pipeline."""
    df = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(df)
    train_model(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    run_training()
