import React from "react";
import { Link } from "react-router-dom";
import ScoreGauge from "../components/ScoreGauge";
import ShapChart from "../components/ShapChart";

export default function Result() {
  const result = JSON.parse(sessionStorage.getItem("creditpulse_result") || "null");

  if (!result) {
    return (
      <div className="form-page shell">
        <div className="form-card" style={{ textAlign: 'center', padding: '48px' }}>
          <div className="eyebrow">No Active Assessment</div>
          <h2>Run Your First Score</h2>
          <p>Submit a credit request to generate a real-time risk score and SHAP explanation.</p>
          <Link className="button" to="/apply" style={{ marginTop: '20px' }}>Start Assessment →</Link>
        </div>
      </div>
    );
  }

  const isAccepted = result.decision === "accepté";

  return (
    <div className="shell">
      <div className="form-header">
        <div className="eyebrow">✨ AI Assessment Complete</div>
        <h1>Credit Risk & SHAP Analysis</h1>
        <p>Real-time prediction generated via XGBoost machine learning model and feature store metrics.</p>
      </div>

      <div className="result-grid">
        {/* Left Score Card */}
        <div className="result-score-card">
          <span className="metric-label">XGBoost Credit Rating</span>
          
          <ScoreGauge score={result.score} />

          <div className={`status-pill ${isAccepted ? 'complete' : 'pending'}`} style={{ fontSize: '0.9rem', padding: '8px 20px', marginTop: '10px' }}>
            Decision: {result.decision.toUpperCase()}
          </div>
        </div>

        {/* Right Details Card */}
        <div className="shap-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>SHAP Feature Explanations</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Est. Default Risk: <strong style={{ color: '#FFF' }}>{(result.probability_default * 100).toFixed(1)}%</strong>
            </span>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Green bars indicate factors that boosted your score; red bars show risk factors that reduced your score.
          </p>

          <ShapChart values={result.explanation} />

          <div style={{ marginTop: '28px', display: 'flex', gap: '14px' }}>
            <Link className="button" to="/apply">Run Another Assessment</Link>
            <Link className="button secondary" to="/dashboard">Back to Dashboard</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
