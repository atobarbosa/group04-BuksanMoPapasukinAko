FROM python:3.13-slim
WORKDIR /app

# Install system dependencies if required by pyarrow/scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt

# Copy application files
COPY preprocessing.py .
COPY api.py .
# Ensure your model and encoders are copied into the image
COPY random_forest_model.pkl .
COPY encoders.pkl .

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]