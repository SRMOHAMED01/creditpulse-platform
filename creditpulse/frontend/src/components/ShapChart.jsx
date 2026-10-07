import React from "react";

export default function ShapChart({ values = [] }) {
  if (!values || !values.length) {
    return <p style={{ color: 'var(--text-muted)' }}>No SHAP explanation signals returned.</p>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', margin: '20px 0' }}>
      {values.map((item, index) => {
        const label = item.feature || item.name || `Feature ${index + 1}`;
        const impact = Number(item.impact ?? item.value ?? 0);
        const isPositive = impact >= 0;
        const widthPct = Math.min(100, Math.max(12, Math.abs(impact) * 100));

        return (
          <div className="shap-item" key={`${label}-${index}`}>
            <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>
              {label.replace('_', ' ')}
            </span>
            
            <div className="shap-bar-track">
              <div
                className={`shap-bar-fill ${isPositive ? 'positive' : 'negative'}`}
                style={{ width: `${widthPct}%` }}
              />
            </div>

            <span style={{ fontSize: '0.85rem', fontWeight: 700, textAlign: 'right', color: isPositive ? '#34D399' : '#F87171' }}>
              {impact > 0 ? '+' : ''}{impact.toFixed(3)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
