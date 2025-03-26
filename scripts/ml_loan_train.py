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
DATA_FILE = os.path.join(BASE_DIR, "data", "loan_approval_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ✅ MLflow Tracking
mlflow.set_experiment("Loan_Approval_Experiment")

def load_data():
    """Loads dataset and ensures all required columns exist."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"❌ Data file not found: {DATA_FILE}")
    
    df = pd.read_csv(DATA_FILE)
    
    # Ensure columns are clean (strip any spaces)
    df.columns = df.columns.str.strip()

    # Print column names to debug
    print(f"✅ Columns in the dataset: {df.columns.tolist()}")
    
    # Ensure all required columns exist
    expected_columns = {
        "loan_id", "no_of_dependents", "education", "self_employed", 
        "income_annum", "loan_amount", "loan_term", "cibil_score", 
        "residential_assets_value", "commercial_assets_value", 
        "luxury_assets_value", "bank_asset_value", "loan_status"
    }
    
    missing_cols = expected_columns - set(df.columns)
    if missing_cols:
        raise ValueError(f"❌ Missing columns in dataset: {missing_cols}")
    
    return df

def preprocess_data(df):
    """Processes dataset & splits into training/testing."""
    # Convert categorical features to numerical
    df["education"] = df["education"].map({"Graduate": 1, "Not Graduate": 0})
    df["self_employed"] = df["self_employed"].map({"Yes": 1, "No": 0})
    
    # Fill missing values for numeric columns with mean
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Fill missing values for categorical columns with mode (most frequent value)
    categorical_cols = df.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Define features (X) and target (y)
    X = df.drop(columns=["loan_id", "loan_status"])  # Remove ID & target column
    y = df["loan_status"]  # Target column

    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(X_train, X_test, y_train, y_test, n_estimators=50, max_depth=5):
    """Trains and logs the model with MLflow."""
    with mlflow.start_run():
        # ✅ Train model
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)

        # ✅ Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        # ✅ Log accuracy
        accuracy = accuracy_score(y_test, model.predict(X_test))
        mlflow.log_metric("accuracy", accuracy)

        # ✅ Save & log model
        model_path = os.path.join(MODEL_DIR, f"loan_model_{n_estimators}_{max_depth}.pkl")
        joblib.dump(model, model_path)
        mlflow.sklearn.log_model(model, "random_forest_loan_model")

        print(f"✅ Model saved: {model_path}")
        print(f"✅ Accuracy: {accuracy:.2%}")

def run_training():
    """Runs the full training pipeline."""
    df = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(df)

    # ✅ Train models with different hyperparameters for comparison
    for n in [10, 50, 100]:
        for depth in [None, 5, 10]:
            train_model(X_train, X_test, y_train, y_test, n_estimators=n, max_depth=depth)

if __name__ == "__main__":
    run_training()
