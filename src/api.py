"""FastAPI backend for the phishing URL detection project."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import analyze_url, load_model
from validation import InvalidURLError

# Web pages that may call this API when no other origins are configured (local development).
LOCAL_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


def get_allowed_origins():
    """Return the web pages that may call this API from a browser.

    The ALLOWED_ORIGINS environment variable holds a comma-separated list, for example
    "https://my-site.vercel.app". If it is empty, only the local development servers are allowed.
    """
    configured = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    return origins or LOCAL_ORIGINS


app = FastAPI(title="Phishing URL Detector")

# Allow only the listed web pages to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

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
    try:
        return analyze_url(model, request.url)
    except InvalidURLError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
