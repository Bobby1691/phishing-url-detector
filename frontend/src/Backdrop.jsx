import { useEffect, useRef } from "react";
import "./Backdrop.css";

const STATE_COLORS = {
  idle: [107, 145, 255],
  scanning: [125, 139, 255],
  legitimate: [99, 202, 166],
  suspicious: [225, 174, 102],
  phishing: [226, 112, 143],
};

function Backdrop({ state }) {
  const canvasRef = useRef(null);
  const stateRef = useRef(state);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return undefined;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let width = 0;
    let height = 0;
    let frameId = 0;
    let lastTime = 0;
    let nodes = [];

    function resize() {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);

      const count = Math.max(28, Math.min(66, Math.round((width * height) / 24000)));
      nodes = Array.from({ length: count }, (_, index) => {
        const side = index % 2 === 0 ? (Math.random() * 0.34) : (0.66 + Math.random() * 0.34);
        return {
          x: side * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.09,
          vy: (Math.random() - 0.5) * 0.09,
          phase: Math.random() * Math.PI * 2,
          radius: Math.random() > 0.88 ? 1.8 : 1.05,
        };
      });
      draw(0, false);
    }

    function draw(time, animate = true) {
      const [red, green, blue] = STATE_COLORS[stateRef.current] || STATE_COLORS.idle;
      ctx.clearRect(0, 0, width, height);

      // Gentle corner light; the center stays darker so the interface remains the focus.
      const leftGlow = ctx.createRadialGradient(0, height * 0.48, 0, 0, height * 0.48, width * 0.58);
      leftGlow.addColorStop(0, `rgba(${red}, ${green}, ${blue}, 0.10)`);
      leftGlow.addColorStop(1, `rgba(${red}, ${green}, ${blue}, 0)`);
      ctx.fillStyle = leftGlow;
      ctx.fillRect(0, 0, width, height);

      const rightGlow = ctx.createRadialGradient(width, height * 0.55, 0, width, height * 0.55, width * 0.58);
      rightGlow.addColorStop(0, "rgba(128, 91, 208, 0.095)");
      rightGlow.addColorStop(1, "rgba(128, 91, 208, 0)");
      ctx.fillStyle = rightGlow;
      ctx.fillRect(0, 0, width, height);

      const maxDistance = Math.max(125, Math.min(185, width * 0.13));
      for (let i = 0; i < nodes.length; i += 1) {
        const node = nodes[i];
        if (animate) {
          node.x += node.vx;
          node.y += node.vy;
          if (node.x < -20 || node.x > width + 20) node.vx *= -1;
          if (node.y < -20 || node.y > height + 20) node.vy *= -1;
        }

        // Fade connections through the central text area; keep the network at the edges.
        const centerFade = Math.min(1, Math.max(0.12, Math.abs(node.x / Math.max(width, 1) - 0.5) * 2.2));
        for (let j = i + 1; j < nodes.length; j += 1) {
          const other = nodes[j];
          const dx = node.x - other.x;
          const dy = node.y - other.y;
          const distance = Math.hypot(dx, dy);
          if (distance < maxDistance) {
            const edgeFade = 1 - distance / maxDistance;
            const opacity = edgeFade * centerFade * (0.12 + 0.05 * Math.sin((time * 0.00025) + node.phase));
            ctx.strokeStyle = `rgba(${red}, ${green}, ${blue}, ${opacity})`;
            ctx.lineWidth = 0.65;
            ctx.beginPath();
            ctx.moveTo(node.x, node.y);
            ctx.lineTo(other.x, other.y);
            ctx.stroke();
          }
        }

        const nodeOpacity = centerFade * (node.radius > 1.5 ? 0.52 : 0.28);
        ctx.beginPath();
        ctx.fillStyle = `rgba(${red}, ${green}, ${blue}, ${nodeOpacity})`;
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function animate(time) {
      if (time - lastTime > 28) {
        draw(time, true);
        lastTime = time;
      }
      frameId = window.requestAnimationFrame(animate);
    }

    resize();
    if (!reduceMotion) frameId = window.requestAnimationFrame(animate);
    window.addEventListener("resize", resize);
    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <div className="backdrop" aria-hidden="true">
      <canvas ref={canvasRef} />
      <div className="backdrop-grain" />
      <div className="backdrop-vignette" />
    </div>
  );
}

export default Backdrop;
