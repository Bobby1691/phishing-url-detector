import { useEffect, useState } from "react";

// Arc segments of the dial. Each one covers a zone of the risk scale:
// 0 to 40 percent, 40 to 80 percent and 80 to 100 percent.
const ZONES = [
  { name: "legitimate", path: "M 20 100 A 80 80 0 0 1 75.28 23.92" },
  { name: "suspicious", path: "M 75.28 23.92 A 80 80 0 0 1 164.72 52.98" },
  { name: "phishing", path: "M 164.72 52.98 A 80 80 0 0 1 180 100" },
];

const COUNT_UP_MS = 1600;

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

// Counts from 0 up to the target value. People who prefer less motion see the final value at once.
function useCountUp(target) {
  const [value, setValue] = useState(() => (prefersReducedMotion() ? target : 0));

  useEffect(() => {
    if (prefersReducedMotion()) return undefined;

    let frameId = 0;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / COUNT_UP_MS, 1);
      const eased = 1 - (1 - progress) ** 3;
      setValue(target * eased);
      if (progress < 1) frameId = requestAnimationFrame(tick);
    }

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [target]);

  return value;
}

function Gauge({ score }) {
  const shown = useCountUp(score);

  // 0 percent points to the left end of the dial and 100 percent to the right end.
  const angle = score * 1.8;

  return (
    <div
      className="gauge"
      role="img"
      aria-label={`Risk score ${score} percent. Below 40 is legitimate, 40 to 80 is suspicious, 80 and above is phishing.`}
    >
      <svg className="gauge-dial" viewBox="0 0 200 118" aria-hidden="true">
        {ZONES.map((zone) => (
          <path key={zone.name} d={zone.path} className={`arc arc-${zone.name}`} />
        ))}
        <text x="20" y="116" className="gauge-tick" textAnchor="middle">0</text>
        <text x="71.6" y="11" className="gauge-tick" textAnchor="middle">40</text>
        <text x="174.4" y="44" className="gauge-tick" textAnchor="middle">80</text>
        <text x="180" y="116" className="gauge-tick" textAnchor="middle">100</text>
        <g className="needle" style={{ "--angle": `${angle}deg` }}>
          <line x1="100" y1="100" x2="34" y2="100" />
        </g>
        <circle className="hub" cx="100" cy="100" r="7" />
      </svg>
      <p className="gauge-value">
        {shown.toFixed(1)}
        <span>%</span>
      </p>
      <p className="gauge-caption">Risk score</p>
    </div>
  );
}

export default Gauge;
