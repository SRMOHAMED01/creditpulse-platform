import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../api/auth";
import client from "../api/client";

const readLastAssessment = () => {
  try {
    return JSON.parse(sessionStorage.getItem("creditpulse_result") || "null");
  } catch {
    return null;
  }
};

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const assessment = useMemo(readLastAssessment, []);

  useEffect(() => {
    Promise.allSettled([getCurrentUser(), client.get("/users/profile")])
      .then(([userResult, profileResult]) => {
        if (userResult.status === "fulfilled") setUser(userResult.value.data);
        if (profileResult.status === "fulfilled") setProfile(profileResult.value.data);
        const unexpectedProfileError = profileResult.status === "rejected"
          && profileResult.reason?.response?.status !== 404;
        setLoadError(userResult.status === "rejected" || unexpectedProfileError);
      })
      .finally(() => setLoading(false));
  }, []);

  const displayName = user?.email?.split("@")[0] || "there";
  const defaultRisk = assessment
    ? `${Math.round(assessment.probability_default * 100)}%`
    : "—";

  return (
    <div className="dashboard-page">
      <section className="dashboard-hero">
        <div>
          <div className="eyebrow">Personal credit workspace</div>
          <h1>Welcome back, <span>{displayName}</span>.</h1>
          <p>Keep your financial profile current and explore the signals behind every assessment.</p>
        </div>
        <Link className="button button-arrow" to={profile ? "/apply" : "/profile"}>
          {profile ? "New assessment" : "Complete profile"}<span aria-hidden="true">↗</span>
        </Link>
      </section>

      {loadError && <div className="notice error">We could not load your workspace. Refresh and try again.</div>}

      <section className="overview-grid" aria-busy={loading}>
        <article className="profile-overview">
          <div className="card-topline">
            <span>Profile readiness</span>
            <span className={`status-pill ${profile ? "complete" : "pending"}`}>
              {loading ? "Checking" : profile ? "Complete" : "Action needed"}
            </span>
          </div>
          <div className="readiness-value">{loading ? "—" : profile ? "100" : "0"}<small>%</small></div>
          <div className="progress-track"><i style={{ width: profile ? "100%" : "6%" }} /></div>
          <p>{profile
            ? "Your financial details are ready for a new assessment."
            : "Add your income, debt, work history and payment habits to continue."}</p>
          <Link className="text-link light" to="/profile">
            {profile ? "Review profile" : "Build profile"} <span aria-hidden="true">→</span>
          </Link>
        </article>

        <article className="metric-card">
          <span className="metric-label">Latest score</span>
          <strong>{assessment?.score ?? "—"}</strong>
          <span className="metric-meta">{assessment ? "out of 100" : "No assessment yet"}</span>
        </article>
        <article className="metric-card">
          <span className="metric-label">Estimated risk</span>
          <strong>{defaultRisk}</strong>
          <span className="metric-meta">Default probability</span>
        </article>
        <article className="metric-card decision-card">
          <span className="metric-label">Latest outcome</span>
          <strong className={assessment ? "decision-value" : ""}>{assessment?.decision || "—"}</strong>
          <span className="metric-meta">Demonstration model</span>
        </article>
      </section>

      <section className="dashboard-lower">
        <article className="next-step-card">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Recommended next step</div>
              <h2>{profile ? "Explore a credit request" : "Complete your financial profile"}</h2>
            </div>
            <span className="step-number">{profile ? "02" : "01"}</span>
          </div>
          <p>{profile
            ? "Run a transparent risk assessment and see which financial signals influenced the result."
            : "Create your reusable financial baseline before requesting an assessment."}</p>
          <div className="next-step-footer">
            <div className="mini-steps" aria-label="Progress">
              <span className="done">Profile</span><i /><span className={assessment ? "done" : ""}>Assessment</span><i /><span>Review</span>
            </div>
            <Link className="button secondary" to={profile ? "/apply" : "/profile"}>Continue</Link>
          </div>
        </article>

        <aside className="insight-card">
          <div className="insight-icon" aria-hidden="true">i</div>
          <div>
            <div className="eyebrow">How to read your result</div>
            <h3>Transparent by design</h3>
            <p>Every assessment includes a risk score, estimated probability and feature-level contributions.</p>
            <Link className="text-link" to={assessment ? "/result" : "/apply"}>
              {assessment ? "Review latest result" : "Learn through an assessment"} <span aria-hidden="true">→</span>
            </Link>
          </div>
        </aside>
      </section>

      <p className="demo-disclaimer">CreditPulse uses synthetic training data and is intended for demonstration—not real lending decisions.</p>
    </div>
  );
}
