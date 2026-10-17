import "@fontsource-variable/figtree";
import { useState } from "react";
import "./App.css";
import Backdrop from "./Backdrop";
import Gauge from "./Gauge";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/analyze";
const REPO_URL = "https://github.com/Bobby1691/phishing-url-detector";
const EXAMPLES = [
  { label: "google.com", tone: "safe" },
  { label: "paypal-secure-login.xyz", tone: "risk" },
  { label: "github.com", tone: "safe" },
];

const LEVELS = {
  Phishing: {
    className: "phishing",
    title: "Phishing detected",
    guidance: "Avoid opening this link or entering personal information.",
  },
  Suspicious: {
    className: "suspicious",
    title: "Looks suspicious",
    guidance: "Treat this link carefully and verify it through a trusted source.",
  },
  Unverified: {
    className: "suspicious",
    title: "Not verified",
    guidance: "No strong phishing indicators were found in the URL, but this domain's reputation has not been verified. Do not treat this result as proof of safety.",
  },
};

function getDomain(address) {
  try {
    const parsed = new URL(address.includes("://") ? address : `https://${address}`);
    return parsed.hostname.replace(/^www\./, "");
  } catch {
    return address;
  }
}

function ShieldMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none">
      <path d="M12 2.7 20 5.8v5.6c0 4.9-3.3 8.5-8 10.2-4.7-1.7-8-5.3-8-10.2V5.8L12 2.7Z" />
      <path d="m8.7 12.1 2.1 2.1 4.6-4.7" />
    </svg>
  );
}

function StatusRow({ icon, label, complete }) {
  return (
    <div className="status-row">
      <span className="status-icon" aria-hidden="true">{icon}</span>
      <span className="status-label">{label}</span>
      <span className={`status-pill ${complete ? "is-complete" : ""}`}>
        {complete ? "READY" : "PENDING"}
      </span>
    </div>
  );
}

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function checkLink(address) {
    const trimmed = address.trim();
    if (!trimmed) {
      setError("Enter a website URL to start the check.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed }),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        setError(typeof data.detail === "string" ? data.detail : "The server could not analyze this URL. Try again.");
        return;
      }

      if (!data.verdict || !Number.isFinite(Number(data.risk_score))) {
        setError("The API response is missing the verdict or risk score.");
        return;
      }

      setResult({
        ...data,
        risk_score: Math.max(0, Math.min(100, Number(data.risk_score))),
        reasons: Array.isArray(data.reasons) ? data.reasons : [],
        domain: getDomain(trimmed),
      });
    } catch {
      setError("Could not reach the API. Start the backend and try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    checkLink(url);
  }

  function handleExample(example) {
    setUrl(example);
    checkLink(example);
  }

  const level = result ? LEVELS[result.verdict] : null;
  const backgroundState = loading ? "scanning" : level?.className || "idle";
  const completed = Boolean(result && level);

  return (
    <>
      <Backdrop state={backgroundState} />
      <div className="site-shell" id="home">
        <header className="topbar">
          <a className="brand" href="#home" aria-label="PhishGuard home">
            <span className="brand-mark"><ShieldMark /></span>
            <span>Phish<span className="brand-accent">Guard</span></span>
          </a>
          <nav className="top-nav" aria-label="Main navigation">
            <a className="nav-link active" href="#home">Home</a>
            <a className="nav-link" href="#about">About</a>
            <a className="nav-link" href="#signals">Signals</a>
            <a className="nav-link" href="#how-it-works">How it works</a>
          </nav>
        </header>

        <main>
          <section className="hero" aria-labelledby="page-title">
            <p className="eyebrow"><span className="eyebrow-dot" /> AI-powered cybersecurity</p>
            <h1 id="page-title">Phishing URL <span>Detector</span></h1>
            <p className="hero-copy">
              A closer look at a link before you trust it.
              <br className="desktop-break" /> Check URL patterns with a machine-learning model.
            </p>

            <div className="search-wrap">
              <form className="url-form" onSubmit={handleSubmit}>
                <span className="link-icon" aria-hidden="true">↗</span>
                <label className="visually-hidden" htmlFor="url-input">Website URL</label>
                <input
                  id="url-input"
                  name="url"
                  type="text"
                  inputMode="url"
                  autoComplete="url"
                  spellCheck={false}
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  placeholder="Enter a website URL (e.g. https://example.com)"
                  aria-describedby="url-hint"
                />
                <button className="check-button" type="submit" disabled={loading}>
                  <span>{loading ? "Checking…" : "Check link"}</span>
                  <span className="button-arrow" aria-hidden="true">↗</span>
                </button>
              </form>
            </div>
            <p className="url-hint" id="url-hint">The link isn’t opened. We analyze basic URL structure only; domain reputation is not checked.</p>

            <div className="examples" aria-label="Example URLs">
              <span className="examples-label">Try an example</span>
              {EXAMPLES.map((example) => (
                <button
                  key={example.label}
                  type="button"
                  className={`example-chip ${example.tone === "risk" ? "chip-risk" : ""}`}
                  disabled={loading}
                  onClick={() => handleExample(example.label)}
                >
                  {example.label}
                </button>
              ))}
            </div>

            {error && <p className="error-message" role="alert">{error}</p>}
          </section>

          <section className={`analysis-card ${level ? `result-${level.className}` : ""}`} aria-label="URL risk analysis" aria-live="polite">
            <div className="gauge-side">
              <Gauge score={result ? result.risk_score : 0} />
              <p className="gauge-footnote">Model-estimated phishing score</p>
            </div>

            <div className="analysis-side">
              <div className="analysis-heading">
                <span className="analysis-shield"><ShieldMark /></span>
                <div>
                  <p className="section-kicker">{completed ? "Analysis complete" : loading ? "Analysis in progress" : "Ready when you are"}</p>
                  <h2>{level ? level.title : loading ? "Checking this URL" : "Scan a URL"}</h2>
                  <p className="analysis-description">
                    {level ? level.guidance : loading
                      ? "The API is evaluating the submitted URL."
                      : "Enter a website address above to see its risk estimate and warning signs."}
                  </p>
                  {result?.domain && <p className="scanned-domain">{result.domain}</p>}
                </div>
              </div>

              <div className="status-list" id="signals">
                <StatusRow icon="↗" label="URL structure" complete={completed} />
                <StatusRow icon="⌘" label="Model classification" complete={completed} />
                <StatusRow icon="◇" label="Risk assessment" complete={completed} />
                <StatusRow icon="≡" label="Warning summary" complete={completed} />
              </div>

              {completed && result.reasons.length > 0 && (
                <div className="reasons-block">
                  <h3>Things to review</h3>
                  <ul>
                    {result.reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>)}
                  </ul>
                </div>
              )}
              {completed && result.reasons.length === 0 && (
                <p className="no-reasons">{result.verdict === "Unverified" ? "No strong URL-level warning signs were found; domain reputation has not been verified." : "No specific warning signs were returned by the model."}</p>
              )}
            </div>
          </section>

          <section className="quiet-details" id="how-it-works">
            <div id="about">
              <span className="detail-number">01</span>
              <h3>Inspect the URL</h3>
              <p>Look for unusual structure, subdomains and other URL-level signals.</p>
            </div>
            <div>
              <span className="detail-number">02</span>
              <h3>Estimate the risk</h3>
              <p>The backend model returns a classification and an estimated risk score.</p>
            </div>
            <div>
              <span className="detail-number">03</span>
              <h3>Review the signals</h3>
              <p>Use the result as guidance, not as a guarantee that a site is safe.</p>
            </div>
          </section>
        </main>

        <footer className="site-footer">
          <span>Made for safer browsing.</span>
          <a href={REPO_URL} target="_blank" rel="noopener noreferrer">View source <span aria-hidden="true">↗</span></a>
        </footer>
      </div>
    </>
  );
}

export default App;
