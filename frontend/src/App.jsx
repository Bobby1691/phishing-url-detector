import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/analyze";

// How each verdict returned by the API is shown on the page.
const LEVELS = {
  Phishing: { className: "phishing", title: "🔴 Phishing Detected" },
  Suspicious: { className: "suspicious", title: "🟡 Suspicious" },
  Legitimate: { className: "legitimate", title: "🟢 Looks Legitimate" },
};

// Text shown when no individual warning sign was found.
const NO_WARNING_TEXT = {
  Phishing: "The model flagged this URL from a combination of features.",
  Suspicious: "No single obvious warning sign was found, but the overall pattern looks unusual.",
  Legitimate: "No obvious warning signs were found in the URL.",
};

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (response.ok) {
        setResult(await response.json());
      } else if (response.status === 400) {
        const data = await response.json();
        setError(data.detail);
      } else {
        setError("The server returned an error. Please try again.");
      }
    } catch {
      setError("Could not reach the API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  const level = result ? LEVELS[result.verdict] : null;

  return (
    <main className="container">
      <h1>Phishing URL Detector</h1>
      <p className="subtitle">Paste a link to check it before you open it.</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://example.com"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Checking..." : "Check URL"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && level && (
        <section className={`result ${level.className}`}>
          <h2>{level.title}</h2>
          <p className="score">Risk Score: {result.risk_score}%</p>

          {result.verdict === "Suspicious" && (
            <p>
              The model is not sure about this URL. Do not enter passwords or
              personal details unless you are certain it is genuine.
            </p>
          )}

          {result.reasons.length > 0 ? (
            <>
              <h3>Warning signs</h3>
              <ul>
                {result.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </>
          ) : (
            <p>{NO_WARNING_TEXT[result.verdict]}</p>
          )}

          <p className="note">
            This is an estimate, not a guarantee of safety. Only the domain part of the URL is analyzed.
          </p>
        </section>
      )}
    </main>
  );
}

export default App;
