FROM python:3.13-slim

WORKDIR /app

COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt

COPY ui.py .

EXPOSE 7860

CMD ["python", "ui.py"]