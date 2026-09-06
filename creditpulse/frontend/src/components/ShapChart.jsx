import React from "react";

export default function ShapChart({ values = [] }) {
  return <div className="shap-chart">{values.length ? values.map((item, index) => {
    const label = item.feature || item.name || `Signal ${index + 1}`;
    const value = Number(item.impact ?? item.value ?? 0);
    return <div className="shap-row" key={`${label}-${index}`}><span>{label}</span><div className="shap-track"><i className={value >= 0 ? "positive" : "negative"} style={{ width: `${Math.min(100, Math.max(8, Math.abs(value) * 100))}%` }} /></div><strong>{value > 0 ? "+" : ""}{value.toFixed(2)}</strong></div>;
  }) : <p>No explanation signals returned.</p>}</div>;
}
