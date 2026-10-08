import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../api/auth";
import client from "../api/client";
import { getCreditApplications } from "../api/credit";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [assessments, setAssessments] = useState([]);
  const [historyError, setHistoryError] = useState(false);
  const [historyOffset, setHistoryOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const assessment = assessments[0];

  const loadMore = async () => {
    setHistoryBusy(true);
    setHistoryError(false);
    try {
      const { data } = await getCreditApplications({ limit: 20, offset: historyOffset });
      setAssessments((previous) => [...previous, ...data]);
      setHistoryOffset((previous) => previous + data.length);
      setHasMore(data.length === 20);
    } catch {
      setHistoryError(true);
    } finally {
      setHistoryBusy(false);
    }
  };

  useEffect(() => {
    let active = true;
    Promise.allSettled([getCurrentUser(), client.get("/users/profile"), getCreditApplications({ limit: 20 })])
      .then(([userResult, profileResult, historyResult]) => {
        if (!active) return;
        if (historyResult.status === "fulfilled") {
          setAssessments(historyResult.value.data);
          setHistoryOffset(historyResult.value.data.length);
          setHasMore(historyResult.value.data.length === 20);
        } else setHistoryError(true);
        if (userResult.status === "fulfilled") setUser(userResult.value.data);
        if (profileResult.status === "fulfilled") setProfile(profileResult.value.data);
        const unexpectedProfileError = profileResult.status === "rejected"
          && profileResult.reason?.response?.status !== 404;
        setLoadError(userResult.status === "rejected" || unexpectedProfileError);
      })
      .catch(() => setLoadError(true))
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const displayName = user?.email?.split("@")[0] || "User";
  const defaultRisk = assessment && typeof assessment.probability_default === "number"
    ? `${Math.round(assessment.probability_default * 100)}%`
    : "—";

  return (
    <div className="dashboard-page shell">
      {/* Hero Header */}
      <section className="dashboard-hero">
        <div>
          <div className="eyebrow">⚡ Live Financial Workspace</div>
          <h1>Welcome back, <span>{displayName}</span></h1>
          <p>Review your saved credit assessments, financial profile, and model explanations.</p>
        </div>
        <Link className="button" to={profile ? "/apply" : "/profile"}>
          {profile ? "+ New Assessment" : "Complete Profile"}
        </Link>
      </section>

      {loadError && (
        <div className="error" style={{ marginBottom: '24px' }}>
          Backend API is unavailable or returning an error. Start the FastAPI backend on http://localhost:8000 to enable live sync.
        </div>
      )}

      {/* Main KPI Grid */}
      <section className="overview-grid" aria-busy={loading}>
        {/* Profile Overview Card */}
        <article className="profile-overview">
          <div className="card-topline">
            <span>Profile Readiness</span>
            <span className={`status-pill ${profile ? "complete" : "pending"}`}>
              {loading ? "Checking..." : profile ? "Complete" : "Action Needed"}
            </span>
          </div>
          <div className="readiness-value">{loading ? "—" : profile ? "100" : "0"}<small>%</small></div>
          <div className="progress-track">
            <i style={{ width: profile ? "100%" : "8%" }} />
          </div>
          <p style={{ marginTop: '16px', fontSize: '0.88rem' }}>
            {profile
              ? "Your financial profile is saved and ready for an assessment."
              : "Complete your income, debt, and employment profiles to unlock scoring."}
          </p>
          <Link className="button secondary" to="/profile" style={{ marginTop: '14px', width: 'fit-content', padding: '0 16px', minHeight: '38px', fontSize: '0.82rem' }}>
            {profile ? "Review Profile →" : "Build Profile →"}
          </Link>
        </article>

        {/* Metric Card 1: Score */}
        <article className="metric-card">
          <span className="metric-label">Credit Score</span>
          <strong>{assessment?.score ?? "—"}</strong>
          <span className="metric-meta">{assessment ? "Out of 100" : "No assessment yet"}</span>
        </article>

        {/* Metric Card 2: Risk */}
        <article className="metric-card">
          <span className="metric-label">Default Risk</span>
          <strong style={{ color: (assessment?.probability_default ?? 0) > 0.3 ? '#F87171' : '#34D399' }}>
            {defaultRisk}
          </strong>
          <span className="metric-meta">XGBoost Probability</span>
        </article>

        {/* Virtual Credit Card Widget */}
        <article className="virtual-card-widget">
          <div>
            <div className="virtual-card-chip"></div>
            <div className="virtual-card-number">•••• •••• •••• {assessment ? "8824" : "0000"}</div>
          </div>
          <div className="virtual-card-holder">
            <div>
              <div style={{ fontSize: '0.65rem', opacity: 0.6 }}>Card Holder</div>
              <div style={{ fontWeight: 700, color: '#FFF' }}>{displayName.toUpperCase()}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.65rem', opacity: 0.6 }}>Tier</div>
              <div style={{ fontWeight: 700, color: '#A855F7' }}>
                {assessment?.decision === 'accepté' ? 'PREMIUM AAA' : 'STANDARD'}
              </div>
            </div>
          </div>
        </article>
      </section>

      {/* Lower Section: Recommendations & History */}
      <section className="dashboard-details">
        <article className="form-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.3rem' }}>Recent Activity & Decision History</h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Saved assessments</span>
          </div>

          {historyError && <p className="error">Could not load assessment history. <button className="button secondary" onClick={loadMore} disabled={loading || historyBusy}>Retry</button></p>}
          {loading ? <p role="status">Loading assessment history...</p> : assessments.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {assessments.map((assessment) => <Link key={assessment.id} to={`/result/${assessment.id}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Assessment #{assessment.id}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{new Date(assessment.created_at).toLocaleString()} · ${assessment.requested_amount.toLocaleString()} · {assessment.duration_months} months</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className={`status-pill ${assessment.decision === 'accepté' ? 'complete' : 'pending'}`}>
                    {(assessment.decision || 'PENDING').toUpperCase()}
                  </div>
                  <div style={{ fontSize: '0.78rem', marginTop: '4px', color: 'var(--text-dim)' }}>Score: {assessment.score ?? '—'}/100</div>
                </div>
              </Link>)}
              {hasMore && <button className="button secondary" onClick={loadMore} disabled={historyBusy}>{historyBusy ? "Loading..." : "Load more"}</button>}
            </div>
          ) : (
            !historyError && <p style={{ color: 'var(--text-muted)' }}>No credit assessment records found. Run your first assessment to populate history.</p>
          )}

          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Ready to run an updated score?</span>
            <Link className="button secondary" to={profile ? "/apply" : "/profile"} style={{ minHeight: '38px', padding: '0 16px', fontSize: '0.82rem' }}>
              Run Assessment →
            </Link>
          </div>
        </article>

        {/* Explainability Insight Card */}
        <article className="form-card" style={{ padding: '28px', background: 'linear-gradient(145deg, rgba(30, 27, 75, 0.4) 0%, rgba(18, 18, 28, 0.9) 100%)', borderColor: 'var(--border-purple)' }}>
          <div className="eyebrow">💡 Model Transparency</div>
          <h3 style={{ fontSize: '1.2rem', margin: '8px 0 12px' }}>Why Explainable AI Matters</h3>
          <p style={{ fontSize: '0.88rem', lineHeight: '1.6' }}>
            CreditPulse leverages SHAP (Shapley Additive exPlanations) to break down every score into clear feature contributions (income impact, DTI ratio impact, payment history).
          </p>
          <Link className="button" to={assessment ? `/result/${assessment.id}` : "/apply"} style={{ marginTop: '20px', width: '100%' }}>
            {assessment ? "View SHAP Breakdown →" : "Start First Assessment"}
          </Link>
        </article>
      </section>

      <p style={{ textAlign: 'center', marginTop: '40px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
        CreditPulse Platform • Demonstration Environment • Powered by React, FastAPI, dbt & XGBoost
      </p>
    </div>
  );
}
