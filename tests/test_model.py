import joblib
from pathlib import Path

# Load the trained model
model_path = Path(__file__).resolve().parent.parent / "models" / "loan_model_50_None.pkl"
model = joblib.load(model_path)

# Define your new data (the features to predict on) [with existing line 18]
# new_data = {
#     "no_of_dependents": [2],
#     "education": [1],  # Graduate (1) or Not Graduate (0)
#     "self_employed": [1],  # Yes (1) or No (0)
#     "income_annum": [500000],
#     "loan_amount": [200000],
#     "loan_term": [15],
#     "cibil_score": [700],
#     "residential_assets_value": [100000],
#     "commercial_assets_value": [50000],
#     "luxury_assets_value": [20000],
#     "bank_asset_value": [150000],
# }

new_data = {
    "no_of_dependents": [17],  # Example number of dependents
    "education": [1],  # Graduate (1)
    "self_employed": [1],  # Yes (1)
    "income_annum": [500000],  # Annual income
    "loan_amount": [1600000],  # Loan amount
    "loan_term": [4],  # Loan term in years
    "cibil_score": [663],  # CIBIL score
    "residential_assets_value": [1300000],  # Residential assets value
    "commercial_assets_value": [100000],  # Commercial assets value
    "luxury_assets_value": [1300000],  # Luxury assets value
    "bank_asset_value": [700000],  # Bank asset value
}

# Convert to DataFrame
import pandas as pd
new_df = pd.DataFrame(new_data)

# Make predictions
predictions = model.predict(new_df)
print(predictions)
