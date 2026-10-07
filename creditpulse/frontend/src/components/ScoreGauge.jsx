import React from "react";

export default function ScoreGauge({ score = 0 }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
  const angle = (safeScore / 100) * 360;

  return (
    <div className="score-arc-container" style={{
      background: `conic-gradient(#8B5CF6 0deg ${angle}deg, rgba(255, 255, 255, 0.08) ${angle}deg 360deg)`,
      borderRadius: '50%',
      padding: '12px',
      boxShadow: '0 0 30px rgba(139, 92, 246, 0.3)'
    }}>
      <div className="score-arc-inner" style={{
        background: '#0B0B14',
        borderRadius: '50%',
        width: '100%',
        height: '100%',
        display: 'grid',
        placeItems: 'center',
        alignContent: 'center'
      }}>
        <div style={{ fontSize: '3.4rem', fontWeight: 800, color: '#FFF' }}>{safeScore}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--purple-neon)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Score Out of 100</div>
      </div>
    </div>
  );
}
