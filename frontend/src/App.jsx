import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/analyze";

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
      if (!response.ok) {
        throw new Error("The server returned an error.");
      }
      setResult(await response.json());
    } catch {
      setError("Could not reach the API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  const isPhishing = result !== null && result.verdict === "Phishing";

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

      {result && (
        <section className={isPhishing ? "result phishing" : "result legitimate"}>
          <h2>{isPhishing ? "🔴 Phishing Detected" : "🟢 Looks Legitimate"}</h2>
          <p className="score">Risk Score: {result.risk_score}%</p>

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
            <p>No obvious warning signs were found in the URL.</p>
          )}

          <p className="note">This is an estimate, not a guarantee of safety. Only the domain part of the URL is analyzed.</p>
        </section>
      )}
    </main>
  );
}

export default App;
