# Phishing URL Detection System

A machine learning project that checks whether a URL looks legitimate or phishing. It shows a risk score and the warning signs found in the URL.

## How it works

1. Features are extracted from the URL text: length, HTTPS, special characters, suspicious words, IP address and number of subdomains.
2. An XGBoost model predicts the probability that the URL is phishing.
3. A FastAPI backend serves the model, and a React frontend shows the result.

The application only analyzes the text of the URL. It never visits the website.

## Results

Evaluated on a 20% test split (47,159 URLs). Precision, recall and F1 are measured for the phishing class.

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Logistic Regression | 0.9602 | 0.9660 | 0.9402 | 0.9529 |
| Random Forest | 0.9715 | 0.9693 | 0.9639 | 0.9666 |
| XGBoost | 0.9713 | 0.9685 | 0.9643 | 0.9664 |

XGBoost is used as the final model. Random Forest performs almost the same.

## Project structure

    data/               Dataset (not included in the repository)
    models/             Trained model
    src/
      features.py       Extracts features from a URL
      build_dataset.py  Builds the feature table from the dataset
      train_model.py    Trains a Logistic Regression baseline
      compare_models.py Compares the three models
      train_final.py    Trains and saves the final model
      predict.py        Returns verdict, risk score and warning signs
      api.py            FastAPI backend
    frontend/           React application

## Setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Run the application

Start the backend from the project folder:

    uvicorn api:app --app-dir src --reload

Start the frontend in a second terminal:

    cd frontend
    npm install
    npm run dev

Then open http://localhost:5173 in your browser.

## Retrain the model (optional)

Download the dataset, place the CSV in a `data/` folder, and run:

    python3 src/build_dataset.py
    python3 src/compare_models.py
    python3 src/train_final.py

## Dataset

PhiUSIIL Phishing URL Dataset: https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset

The dataset is not included in this repository. Please check the dataset page for its authors and license.

## Limitations

- This tool gives a risk estimate, not a guarantee. It can wrongly flag safe websites and can miss real phishing sites.
- The scores above are measured on one dataset. Real-world URLs may behave differently.
- The model uses only six simple URL features.
- The warning signs shown to the user are simple rules. They show which suspicious signs are present, not exactly why the model made its decision.

## Ethics

This project is for defense only. It must not be used to create or improve phishing pages. User-entered URLs should not be stored or shared without consent.

## Future work

- More URL and domain features
- Browser extension that warns about suspicious sites
