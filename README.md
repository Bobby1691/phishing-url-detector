# Phishing URL Detection System

A machine learning project that checks whether a URL looks legitimate or phishing. It shows a risk score and the warning signs found in the URL.

## How it works

1. Features are extracted from the scheme and domain of the URL: HTTPS, domain length, dots, hyphens, digits, "@" symbol, suspicious words, raw IP address and number of subdomains.
2. An XGBoost model predicts the probability that the URL is phishing.
3. A FastAPI backend serves the model, and a React frontend shows the result.

The application only analyzes the text of the URL. It never visits the website. The path and query part of the URL are ignored on purpose (see "Dataset bias" below).

## Results

Evaluated on a 20% test split (47,159 URLs). Precision, recall and F1 are measured for the phishing class.

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Logistic Regression | 0.9086 | 0.9746 | 0.8075 | 0.8832 |
| Random Forest | 0.9386 | 0.9740 | 0.8802 | 0.9247 |
| XGBoost | 0.9386 | 0.9749 | 0.8793 | 0.9246 |

XGBoost is used as the final model. Random Forest performs almost the same. When the model reports phishing it is right about 97.5% of the time, but it misses about 12% of real phishing URLs.

## Dataset bias

An earlier version of this project also used path and query features and reached about 0.995 accuracy. That score was misleading. In the training dataset, almost none of the legitimate URLs has a path or a query string (they are mostly homepages), while about 27% of the phishing URLs do. The model learned "has a path means phishing" and flagged normal links such as Wikipedia articles as phishing with 100% risk.

For this reason only the scheme and the domain are analyzed now. In the same dataset almost all legitimate URLs use HTTPS, so the model may treat plain HTTP as a strong phishing signal even for old but legitimate websites.

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

Restart the backend after retraining so that it loads the new model.

## Dataset

PhiUSIIL Phishing URL Dataset: https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset

The dataset is not included in this repository. Please check the dataset page for its authors and license.

## Limitations

- This tool gives a risk estimate, not a guarantee. It can wrongly flag safe websites and can miss real phishing sites.
- The scores above are measured on one dataset. Real-world URLs may behave differently.
- Only the domain is analyzed, so a phishing page hosted on a trusted domain cannot be detected.
- The model uses only ten simple domain features.
- The warning signs shown to the user are simple rules. They show which suspicious signs are present, not exactly why the model made its decision.

## Ethics

This project is for defense only. It must not be used to create or improve phishing pages. User-entered URLs should not be stored or shared without consent.

## Future work

- More domain features, such as domain age
- A better balanced dataset with realistic legitimate URLs
- Browser extension that warns about suspicious sites
