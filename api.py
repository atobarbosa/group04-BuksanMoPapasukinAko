# api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import io
import csv
import os
from datetime import datetime, timezone
import uvicorn

from preprocessing import encode_with_fallback, split_features_and_target

app = FastAPI(title="BuksanMoPapasukinAko API")

# ── CORS ──────────────────────────────────────────────────────────────────
# Needed once the Gradio UI and this API run in separate Docker containers
# (different origins). Locked to localhost/common dev ports for now;
# tighten this list to your actual frontend origin(s) in production.

allowed_origins = os.getenv("CORS_ORIGINS", "http://127.0.0.1:7860,http://localhost:7860").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Upload safety limit ──────────────────────────────────────────────────
# Prevents a huge or malicious .parquet upload from hanging/crashing the
# server. 50 MB comfortably covers realistic single-scan log files.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

# ── Scan history (plain CSV — no database, per project constraints) ──────
HISTORY_FILE = "scan_history.csv"
HISTORY_FIELDS = ["timestamp", "filename", "total_scanned", "anomalies_detected", "is_network_safe"]


def log_scan_to_history(filename: str, total: int, attacks: int, safe: bool) -> None:
    """Append a single scan result as a row in scan_history.csv (creates the file with a header on first run)."""
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "filename": filename,
            "total_scanned": total,
            "anomalies_detected": attacks,
            "is_network_safe": safe,
        })


def read_scan_history(limit: int = 10) -> list:
    """Return the most recent `limit` scans, newest first. Empty list if no history yet."""
    if not os.path.isfile(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, mode="r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return list(reversed(rows))[:limit]


print("Loading the Brain and Translators...")
model = joblib.load("random_forest_model.pkl")
encoders = joblib.load("encoders.pkl")


@app.post("/scan")
async def scan_network_log(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".parquet"):
            return {"status": "Error", "message": "Invalid file type. Please upload a .parquet file."}

        contents = await file.read()

        if len(contents) > MAX_UPLOAD_BYTES:
            return {
                "status": "Error",
                "message": f"File too large. Max allowed size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
            }

        df = pd.read_parquet(io.BytesIO(contents))

        # Keep a copy of attack_cat (if present) BEFORE it gets dropped as a
        # leakage column. This is ground-truth attack-type info only found in
        # labeled datasets (e.g. UNSW-NB15 test set) — never used as a model
        # feature, purely surfaced afterward as informational context.
        attack_cat_raw = df["attack_cat"].copy() if "attack_cat" in df.columns else None

        # Safely translate text columns using the shared preprocessing logic
        df = encode_with_fallback(df, encoders)

        # Drop leakage columns and align feature order to what the model expects
        feature_order = model.feature_names_in_ if hasattr(model, "feature_names_in_") else None
        X, _ = split_features_and_target(df, feature_order=feature_order)

        predictions = model.predict(X)

        total_scanned = len(predictions)
        # Convert the tiny array to standard Python integers before summing
        total_attacks = int(predictions.astype(int).sum())
        is_safe = bool(total_attacks == 0)

        # Build an attack-category breakdown ONLY if the uploaded file carried
        # ground-truth attack_cat labels (won't exist for real unlabeled traffic).
        attack_cat_breakdown = None
        if attack_cat_raw is not None:
            flagged_mask = predictions.astype(bool)
            if flagged_mask.any():
                counts = attack_cat_raw[flagged_mask].value_counts()
                attack_cat_breakdown = {str(k): int(v) for k, v in counts.items()}

        log_scan_to_history(file.filename, total_scanned, total_attacks, is_safe)

        response = {
            "status": "Success",
            "total_events_scanned": total_scanned,
            "anomalies_detected": total_attacks,
            "is_network_safe": is_safe,
        }
        if attack_cat_breakdown is not None:
            response["attack_category_breakdown"] = attack_cat_breakdown

        return response
    except Exception as e:
        return {"status": "Error", "message": str(e)}


@app.get("/history")
async def get_scan_history(limit: int = 10):
    """Return the most recent scans logged to scan_history.csv, newest first."""
    try:
        return {"status": "Success", "history": read_scan_history(limit=limit)}
    except Exception as e:
        return {"status": "Error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)