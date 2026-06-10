# BuksanMoPapasukinAko : Network Intrusion Anomaly Detector

This is a machine learning project that detects network anomalies. It is a web application that takes network traffic logs in a CSV file and predicts if the traffic is normal background data or a cyberattack.

Manually reading network logs takes to much time for IT administrators. This project try to solve that by using a Random Forest model to classify the data automatically. We built a simple frontend where a user upload a CSV file and get the results on their screen. The frontend and backend run inside Docker containers so it wont have dependency issues when running on different computers.

## Contributors

* AJ Timothy Barbosa (GitHub: atobarbosa)
* John David Villota (GitHub: jdvillota)

## Technologies Used

* **Python 3.11**: Core programming language.
* **Scikit-Learn**: Used for the Random Forest Classifier.
* **Pandas**: Used for reading and preprocessing the CSV data.
* **FastAPI**: Backend server that handles the model predictions.
* **Gradio**: Frontend web interface for file uploads.
* **Docker & Docker Compose**: Used for packaging and running the application.

## Dataset

We trained our machine learning model using the UNSW-NB15 dataset from Kaggle. It contains metadata of normal network traffic and different types of simulated attacks.

## How to Run the Project

You need to have Docker and Docker Compose installed on your machine before running this.

1. Clone this repository:
```bash
git clone [https://github.com/atobarbosa/group04-BuksanMoPapasukinAko](https://github.com/atobarbosa/group04-BuksanMoPapasukinAko)
cd buksanmopapasukinako

```

2. Start the application using Docker:

```bash
docker-compose up --build

```

3. Open the web interface:
Once the containers are running, open your web browser and go to `http://localhost:7860` to access the Gradio upload page.

