# Phishing URL Detection System

A machine learning project that checks whether a URL looks legitimate or phishing, and shows a risk score with the reasons behind it.

## Status
Work in progress. Currently building URL feature extraction.

## Dataset
PhiUSIIL Phishing URL Dataset: https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset

The dataset is not included in this repository. Download it from the link above and place the CSV in a `data/` folder. Please check the dataset page for its authors and license.

## Setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Limitations
This tool gives a risk estimate, not a guarantee. It can wrongly flag safe websites and can miss real phishing sites. Do not rely on it as your only protection.

## Ethics
This project is for defense only. It must not be used to create or improve phishing pages. User-entered URLs should not be stored or shared without consent.
