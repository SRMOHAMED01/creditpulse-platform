import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCreditApplication, getCreditApplications } from "../api/credit";
import ScoreGauge from "../components/ScoreGauge";
import ShapChart from "../components/ShapChart";

export default function Result() {
  const { applicationId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setResult(null);
    setError("");
    const request = applicationId ? getCreditApplication(applicationId) : getCreditApplications({ limit: 1 });
    request.then(({ data }) => {
      if (active) setResult(applicationId ? data : data[0] || null);
    }).catch((failure) => {
      if (active) setError(failure.response?.status === 404 ? "Assessment not found." : "Could not load this assessment. Please try again.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [applicationId, attempt]);

  if (loading) return <div className="form-page shell" role="status">Loading saved assessment...</div>;
  if (error) return <div className="form-page shell"><p className="error">{error}</p><button className="button secondary" onClick={() => setAttempt((value) => value + 1)}>Retry</button><Link className="button secondary" to="/dashboard">Back to Dashboard</Link></div>;

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
        <p>Assessment #{result.id} · {new Date(result.created_at).toLocaleString()} · ${result.requested_amount.toLocaleString()} over {result.duration_months} months</p>
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
            Red bars increase predicted default risk; green bars decrease it. Contributions are measured in log-odds, not percentage points.
          </p>

          <ShapChart values={result.explanation} />
          {result.input_snapshot && <details style={{ marginTop: '20px' }}><summary>Financial inputs used</summary><dl>{Object.entries(result.input_snapshot).map(([key, value]) => <React.Fragment key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{value}</dd></React.Fragment>)}</dl></details>}
          {result.model_version && <details style={{ marginTop: '16px' }}><summary>Model version</summary><p style={{ overflowWrap: 'anywhere' }}>{result.model_version}</p></details>}

          <div style={{ marginTop: '28px', display: 'flex', gap: '14px' }}>
            <Link className="button" to="/apply">Run Another Assessment</Link>
            <Link className="button secondary" to="/dashboard">Back to Dashboard</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
