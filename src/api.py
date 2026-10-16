"""FastAPI backend for the phishing URL detection project."""

from fastapi import FastAPI
from pydantic import BaseModel

from predict import analyze_url, load_model

app = FastAPI(title="Phishing URL Detector")

# Load the model once when the server starts.
model = load_model()


class URLRequest(BaseModel):
    """The data a client must send: a single URL string."""

    url: str


@app.get("/")
def home():
    """Simple check that the server is running."""
    return {"message": "Phishing URL Detector API is running."}


@app.post("/analyze")
def analyze(request: URLRequest):
    """Return the verdict, risk score and warning signs for a URL."""
    return analyze_url(model, request.url)
