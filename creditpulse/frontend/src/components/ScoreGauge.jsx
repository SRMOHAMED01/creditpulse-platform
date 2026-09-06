import React from "react";

export default function ScoreGauge({ score = 0 }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
  return <div className="score-gauge" style={{ "--score-angle": `${safeScore * 1.8}deg` }}>
    <div className="score-gauge-inner"><strong>{safeScore}</strong><span>/ 100</span></div>
  </div>;
}
