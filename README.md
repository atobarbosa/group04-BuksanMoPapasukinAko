# BuksanMoPapasukinAko : Network Intrusion Anomaly Detector

This is a machine learning project that detects network anomalies. It is a containerized web application that takes network traffic logs and predicts if the traffic is normal background data or a cyberattack. 

Manually reading network logs takes to much time for IT administrators. This project try to solve that by using a Random Forest model to classify the data automatically. We built a simple frontend where a user upload a .parquet file and get the results on their screen. The entire application runs inside Docker containers so it wont have dependency issues on different machines.

## Contributors

* AJ Timothy Barbosa (GitHub: atobarbosa)
* John David Villota (GitHub: jdvillota)

## Technologies & Dependencies

* **Python 3.11**: Core programming language.
* **Docker & Docker Compose**: Used for packaging and running the application in isolated environments.
* **scikit-learn**: Used for the Random Forest Classifier.
* **pandas & pyarrow**: Used for reading and preprocessing the tabular dataset.
* **fastapi & uvicorn**: Backend server that handles the machine learning predictions.
* **gradio & python-multipart**: Frontend web interface for file uploads.
* **joblib**: Used for saving and loading the trained model files.

## System Architecture

The project uses a containerized 3-Tier Architecture:
1. **Presentation Layer**: A Gradio web interface container that allows users to upload network logs and view anomaly reports.
2. **Logic Layer**: A FastAPI server container that preprocesses the incoming data, handles unseen network protocols safely, and runs the data through the trained Random Forest model.
3. **Data Access Layer**: In-memory processing of the uploaded tabular files.

## Dataset

We trained our machine learning model using the UNSW-NB15 dataset. It contains metadata of normal network traffic and different types of simulated attacks. We utilize the compressed `.parquet` version of the dataset for faster read times and to prevent data leakage.

## How to Run the Project

You must have Docker and Docker Compose installed on your computer to run this application. You do not need to install Python locally.

1. Clone this repository:
git clone https://github.com/atobarbosa/network-anomaly-detector.git
cd network-anomaly-detector

2. Build and start the Docker containers:
docker-compose up --build

3. Access the application:
Once the terminal shows that both the API and UI containers are running, open your web browser and go to `http://localhost:7860`. Upload your network log file to scan the network.# BuksanMoPapasukinAko : Network Intrusion Anomaly Detector

This is a machine learning project that detects network anomalies. It is a web application that takes network traffic logs and predicts if the traffic is normal background data or a cyberattack. 

Manually reading network logs takes to much time for IT administrators. This project try to solve that by using a Random Forest model to classify the data automatically. We built a simple frontend where a user upload a .parquet file and get the results on their screen.

## Contributors

* AJ Timothy Barbosa (GitHub: atobarbosa)
* John David Villota (GitHub: jdvillota)

## Technologies Used

* **Python 3.11**: Core programming language.
* **Scikit-Learn**: Used for the Random Forest Classifier.
* **Pandas & PyArrow**: Used for reading and preprocessing the tabular data.
* **FastAPI**: Backend server that handles the machine learning predictions.
* **Gradio**: Frontend web interface for file uploads.

## System Architecture

The project uses a 3-Tier Architecture:
1. **Presentation Layer**: A Gradio web interface that allows users to upload network logs and view anomaly reports.
2. **Logic Layer**: A FastAPI server that preprocesses the incoming data, handles unseen network protocols safely, and runs the data through the trained Random Forest model.
3. **Data Access Layer**: In-memory processing of the uploaded tabular files.

## Dataset

We trained our machine learning model using the UNSW-NB15 dataset. It contains metadata of normal network traffic and different types of simulated attacks. We utilize the compressed `.parquet` version of the dataset for faster read times and better memory management.

## How to Run the Project Locally

1. Clone this repository:
git clone https://github.com/atobarbosa/network-anomaly-detector.git
cd network-anomaly-detector

2. Create and activate a virtual environment (we recommend using `uv`):
uv venv
.venv\Scripts\activate

3. Install the dependencies:
uv pip install pandas scikit-learn fastapi uvicorn gradio python-multipart joblib pyarrow

4. Train the model (You only need to do this once):
python train.py

5. Start the backend API:
python api.py

6. Open a new terminal, activate the environment, and start the frontend:
python ui.py

Once the servers are running, open your web browser and go to the local Gradio link provided in the terminal to upload your network logs.
