# train.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

from preprocessing import split_features_and_target

print("1. Loading Parquet Dataset...")
df = pd.read_parquet("data/UNSW_NB15_training-set.parquet")

print("2. Translating text columns into numbers...")
encoders = {}
# Find any column that contains text and convert it to numbers
for col in df.select_dtypes(include=["object", "category"]).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le  # Save the translator to use later!

# Separate the answers ('label') from the test questions using the
# shared leakage-safe split (drops 'id', 'label', 'attack_cat')
X, y = split_features_and_target(df)

print("3. Training the Random Forest (This uses all your CPU cores)...")
# n_jobs=-1 tells the model to train as fast as possible using your whole CPU
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X, y)

print("4. Saving the Brain and Translators to disk...")
joblib.dump(model, "random_forest_model.pkl")
joblib.dump(encoders, "encoders.pkl")
print("Training Complete! You never have to run this script again.")