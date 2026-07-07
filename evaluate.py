# evaluate.py
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

from preprocessing import encode_with_fallback, split_features_and_target

print("1. Loading Test Data and Saved Model...")
# Load the testing dataset (the unseen data)
df_test = pd.read_parquet("data/UNSW_NB15_testing-set.parquet")
model = joblib.load("random_forest_model.pkl")
encoders = joblib.load("encoders.pkl")

print("2. Preprocessing Test Data...")
df_test = encode_with_fallback(df_test, encoders)

feature_order = model.feature_names_in_ if hasattr(model, "feature_names_in_") else None
X_test, y_test = split_features_and_target(df_test, feature_order=feature_order)

print("3. Running Predictions...")
y_pred = model.predict(X_test)

print("\n--- FINAL MODEL REPORT ---")
print(f"Accuracy:  {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(f"Precision: {precision_score(y_test, y_pred) * 100:.2f}% (How often it's right when it flags 'Attack')")
print(f"Recall:    {recall_score(y_test, y_pred) * 100:.2f}% (How many total attacks it actually caught)")

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"True Negatives (Normal labeled Normal): {cm[0][0]}")
print(f"False Positives (Normal labeled Attack): {cm[0][1]}")
print(f"False Negatives (Attack labeled Normal): {cm[1][0]}")
print(f"True Positives (Attack labeled Attack): {cm[1][1]}")