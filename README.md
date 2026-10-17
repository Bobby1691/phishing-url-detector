# Phishing URL Detection System

A machine learning project that checks whether a URL looks legitimate or phishing. It shows a risk score and the warning signs found in the URL.

## How it works

1. Features are extracted from the scheme and domain of the URL: HTTPS, domain length, dots, hyphens, digits, "@" symbol, suspicious words, raw IP address and number of subdomains. A leading "www." is removed, so "example.com" and "www.example.com" give the same result.
2. An XGBoost model predicts the probability that the URL is phishing.
3. A FastAPI backend serves the model, and a React frontend shows the result.

The application only analyzes the text of the URL. It never visits the website. The path and query part of the URL are ignored on purpose (see "Dataset bias" below).

## Results

Evaluated on a 20% test split (47,159 URLs). Precision, recall and F1 are measured for the phishing class.

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Logistic Regression | 0.9172 | 0.9660 | 0.8361 | 0.8964 |
| Random Forest | 0.9297 | 0.9646 | 0.8676 | 0.9135 |
| XGBoost | 0.9298 | 0.9653 | 0.8673 | 0.9136 |

XGBoost is used as the final model. Random Forest performs almost the same. When the model reports phishing it is right about 96.5% of the time, but it misses about 13% of real phishing URLs.

## Dataset bias

The training dataset contains shortcuts that make a model look better than it really is. Three of them were found while testing with real websites:

- **Path and query.** Almost none of the legitimate URLs has a path or a query string (they are mostly homepages), while about 27% of the phishing URLs do. A version that used these features reached about 0.995 accuracy, but it flagged normal links such as Wikipedia articles as phishing with 100% risk. Path and query features were removed.
- **"www." prefix.** No legitimate URL in the dataset is a bare domain without "www.". The model therefore flagged github.com, python.org and wikipedia.org as phishing with 100% risk while accepting their "www." versions. A leading "www." is now removed before features are computed.
- **HTTPS.** Almost all legitimate URLs in the dataset use HTTPS, so the model may treat plain HTTP as a strong phishing signal, even for old but legitimate websites.

Each shortcut was found by testing the model on real URLs, not by the test score, which stayed high.

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
- Legitimate websites with a real subdomain can get a borderline score. In a manual test, https://mail.google.com/ received about 59% risk and was reported as phishing.
- Only the domain is analyzed, so a phishing page hosted on a trusted domain cannot be detected.
- The model uses only ten simple domain features.
- The warning signs shown to the user are simple rules. They show which suspicious signs are present, not exactly why the model made its decision.

## Ethics

This project is for defense only. It must not be used to create or improve phishing pages. User-entered URLs should not be stored or shared without consent.

## Future work

- A middle "suspicious" level for scores close to 50%
- More domain features, such as domain age
- A better balanced dataset with realistic legitimate URLs
- Browser extension that warns about suspicious sites
