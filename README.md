# Phishing URL Detection System

A machine-learning-based phishing URL detection system that analyzes URL characteristics and predicts phishing risk. It provides a verdict, risk score, and human-readable warning signs.

## How It Works

1. **URL parsing:** Normalizes and parses URL components, including scheme, hostname, path, query, and fragment.
2. **Feature extraction:** Extracts URL characteristics using a deterministic, versioned feature schema.
3. **Prediction:** The existing XGBoost model predicts phishing probability using the original V1 feature schema.
4. **API:** FastAPI exposes the prediction endpoint.
5. **Frontend:** React displays the analysis results.

The application analyzes URL text only. It does not visit the submitted website, perform DNS lookups, or make external requests during URL feature extraction.

URLs without a scheme are interpreted as HTTPS. Internationalized domain names (IDNs) are supported through IDNA conversion.

## Feature Engineering

The feature extraction pipeline supports two schemas.

### V1 — Original model-compatible schema

V1 contains the original ten features:

| Feature | Description |
|---|---|
| `has_https` | Whether the URL uses HTTPS |
| `domain_length` | Hostname length |
| `num_dots` | Number of dots in the hostname |
| `num_hyphens` | Number of hyphens in the hostname |
| `num_digits` | Number of digits in the hostname |
| `digit_ratio` | Ratio of digits to hostname length |
| `has_at_symbol` | Whether the URL authority contains `@` |
| `has_suspicious_word` | Whether the hostname contains configured suspicious words |
| `has_ip_address` | Whether the hostname is an IP address |
| `num_subdomains` | Number of subdomains |

V1 is the default schema to preserve compatibility with the existing trained model.

### V2 — Advanced URL feature schema

V2 preserves the original ten features and adds fifteen advanced features:

| Feature | Description |
|---|---|
| `url_length` | Total original URL length |
| `hostname_length` | ASCII hostname length |
| `path_length` | URL path length |
| `query_param_count` | Number of query parameters |
| `special_char_count` | Number of non-alphanumeric URL characters |
| `hostname_entropy` | Shannon entropy of the hostname |
| `has_punycode` | Whether the hostname contains Punycode labels |
| `has_unicode_hostname` | Whether the original hostname contains Unicode |
| `has_percent_encoding` | Whether percent encoding is present |
| `has_malformed_percent_encoding` | Whether malformed percent encoding is present |
| `is_url_shortener` | Whether the hostname matches a configured URL shortener |
| `has_suspicious_tld` | Whether the public suffix matches the configured indicator list |
| `has_brand_impersonation` | Whether configured brand tokens appear outside legitimate brand domains |
| `hostname_complexity` | Ratio of digits, hyphens, and dots in the hostname |
| `has_suspicious_keyword_pattern` | Whether suspicious keyword tokens appear in the decoded URL |

V2 uses the Public Suffix List through `tldextract`. Remote suffix-list downloads are disabled, so parsing does not require network access.

Brand indicators, suspicious TLDs, and URL shortener domains are maintained in `src/brand_config.py`.

**Important:** These features are heuristic indicators, not proof that a URL is malicious. In particular, a brand name or suspicious keyword appearing in a URL does not automatically mean that the URL is phishing.

### Feature schema compatibility

Feature schemas are defined in `src/feature_schema.py`.

- V1 contains 10 features.
- V2 contains 25 features.
- Feature ordering is deterministic.
- Unsupported schema versions are rejected.
- The existing prediction pipeline explicitly uses V1.
- Models trained with a different feature count or ordering are rejected.

Do not use V2 feature vectors with the existing V1 model. V2 model training and deployment require a separate retraining and compatibility update.

## Dataset Processing

The dataset builder supports explicit schema selection.

Build the original V1 dataset:

```bash
python src/build_dataset.py
```

Build the expanded V2 dataset:

```bash
python src/build_dataset.py --schema-version v2
```

Output files:

| Schema | Feature file |
|---|---|
| V1 | `data/processed/features.csv` |
| V2 | `data/processed/features_v2.csv` |

A corresponding metadata JSON file records the schema version, feature names, label column, row count, and source file.

The builder validates URL values, labels, and required dataset columns before generating features.

## Results

Evaluated on a 20% test split (47,159 URLs). Precision, recall, and F1 are measured for the phishing class.

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Logistic Regression | 0.9172 | 0.9660 | 0.8361 | 0.8964 |
| Random Forest | 0.9297 | 0.9646 | 0.8676 | 0.9135 |
| XGBoost | 0.9298 | 0.9653 | 0.8673 | 0.9136 |

XGBoost is used as the final model. These results describe the existing model and dataset; they are not performance results for the new V2 feature schema.

## Decision Levels

The risk score represents the model's estimated phishing probability.

| Risk score | Verdict |
|---|---|
| 80% or more | Phishing |
| 40% to below 80% | Suspicious |
| Below 40% | Unverified |

A low risk score does not guarantee that a website is legitimate.

## Project Structure

```text
data/                  Dataset and processed feature files
models/                Trained model
src/
  api.py               FastAPI backend
  brand_config.py      Brand, TLD, and URL shortener configuration
  build_dataset.py     Versioned dataset feature builder
  feature_schema.py    Feature schema definitions
  features.py          V1 and V2 feature extraction
  predict.py            Model prediction and compatibility checks
  url_normalizer.py    URL normalization
  url_parser.py        Structured URL parsing and IDN support
  validation.py        URL input validation
  train_model.py       Logistic Regression baseline training
  compare_models.py    Model comparison
  train_final.py       Final model training
  threshold_report.py  Threshold evaluation
tests/                 Automated tests
frontend/              React application
requirements.txt       Python dependencies
README.md              Project documentation
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify dependencies:

```bash
python -m pip check
```

## Run the Application

Start the backend from the repository root:

```bash
uvicorn api:app --app-dir src --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Run Tests

Run the complete test suite:

```bash
python -m pytest -q
```

Run API tests:

```bash
python -m pytest tests/test_api.py -v
```

Run feature extraction tests:

```bash
python -m pytest tests/test_features.py -v
```

## Model Compatibility and Retraining

The currently deployed model uses the original V1 feature schema.

The prediction pipeline validates model feature count and feature names before prediction. Incompatible models are rejected instead of silently receiving incorrectly ordered features.

V2 feature extraction is available for dataset generation and evaluation. Before deploying a V2 model:

1. Prepare a suitable dataset.
2. Generate V2 features.
3. Update and verify the training pipeline to use the V2 schema.
4. Train a new model.
5. Validate model feature names and ordering.
6. Evaluate the model on an appropriate held-out dataset.
7. Update prediction compatibility checks before deployment.

Do not replace the existing model with a V2 model until these steps are completed.

## Dataset

PhiUSIIL Phishing URL Dataset:

https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset

The dataset is not included in this repository. Refer to the dataset page for its authorship and license.

## Limitations

- The system provides a risk estimate, not a guarantee of safety.
- Model performance depends on the quality and representativeness of its training data.
- Suspicious keywords, brand indicators, TLDs, and URL shorteners can produce false positives.
- A legitimate website can contain words such as `login`, `account`, or `secure`.
- A phishing page hosted on a trusted domain may not be detected.
- The current prediction model uses V1 features only.
- The application does not verify domain registration, website reputation, or live website behavior.
- The warning signs are rule-based explanations and do not represent the model's complete reasoning.

## Ethics

This project is intended for defensive security research and phishing detection.

It must not be used to create or improve phishing pages. User-submitted URLs should not be stored or shared without appropriate consent.

## Future Work

- Retrain and evaluate a model using V2 features.
- Improve dataset balance and real-world representation.
- Evaluate brand impersonation and suspicious URL patterns.
- Add domain reputation and registration-age analysis.
- Develop a browser extension for suspicious URL warnings.

## License

The code in this repository is released under the MIT License. See the `LICENSE` file.

The dataset is not included in the repository and is governed by its own license.
