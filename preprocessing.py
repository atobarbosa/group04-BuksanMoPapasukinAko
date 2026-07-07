# preprocessing.py
"""
Shared preprocessing logic for BuksanMoPapasukinAko.

Used by train.py, evaluate.py, and api.py so the exact same encoding
and column-dropping rules apply everywhere. Previously this logic was
copy-pasted in three files and had already drifted slightly between
api.py (vectorized .isin()) and evaluate.py (.apply() row-by-row).
"""

import pandas as pd

# Columns that must never be used as model features.
# - 'label' and 'attack_cat' are the prediction targets (dropping both
#   prevents leakage, since attack_cat also gives away the label).
# - 'id' is a row identifier with no predictive value.
LEAKAGE_COLUMNS = ["label", "id", "attack_cat"]


def encode_with_fallback(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    """
    Apply fitted LabelEncoders to a dataframe, safely handling any
    category value the encoder has never seen before (data drift).

    Unseen values are mapped to encoder.classes_[0] instead of raising
    an error, so the API never crashes on unexpected/novel network
    traffic labels.

    Mutates and returns the same dataframe for convenience.
    """
    for col, le in encoders.items():
        if col not in df.columns:
            continue

        col_data = df[col].astype(str)
        known_classes = set(le.classes_)
        safe_default = le.classes_[0]

        # Vectorized: swap any unseen category to the safe default
        col_data = col_data.where(col_data.isin(known_classes), safe_default)
        df[col] = le.transform(col_data)

    return df


def split_features_and_target(df: pd.DataFrame, feature_order=None):
    """
    Drop leakage columns and return (X, y).

    If feature_order is provided (e.g. model.feature_names_in_), X's
    columns are forced into that exact order so predictions never
    silently misalign due to column ordering differences.

    y is None if 'label' isn't present in df (e.g. inference-only data).
    """
    X = df.drop(columns=LEAKAGE_COLUMNS, errors="ignore")

    if feature_order is not None:
        X = X[feature_order]

    y = df["label"] if "label" in df.columns else None
    return X, y
