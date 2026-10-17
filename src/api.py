"""FastAPI backend for the phishing URL detection project."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import analyze_url, load_model
from validation import InvalidURLError

app = FastAPI(title="Phishing URL Detector")

# Allow only the React development server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
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
