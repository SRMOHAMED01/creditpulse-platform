import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/auth";
import { getApiErrorMessage } from "../api/errors";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { data } = await register(form);
      localStorage.setItem("creditpulse_token", data.access_token);
      navigate("/profile");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to create your account."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-hero">
        <div className="eyebrow">🚀 Get Started</div>
        <h1>Unlock Clear <span>Financial Insights.</span></h1>
        <p>Create your free account today. Experience modern credit risk analysis powered by Machine Learning and dbt Data Engineering.</p>
        
        <div className="auth-features">
          <div className="feature-pill">
            <span className="feature-pill-icon">📊</span>
            <span>Instant Risk Score (0-100 Gauge)</span>
          </div>
          <div className="feature-pill">
            <span className="feature-pill-icon">🚀</span>
            <span>Event-driven Kafka Architecture</span>
          </div>
        </div>
      </div>

      <div className="auth-card">
        <div className="form-header">
          <div className="eyebrow">Registration</div>
          <h2>Create Account</h2>
          <p>Set up your credit workspace in seconds</p>
        </div>

        <form onSubmit={submit}>
          <div className="field-grid">
            <div className="field">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="name@example.com"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password (min 8 chars)</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
          </div>

          {error && <div className="error">{error}</div>}

          <div className="form-footer">
            <p>Already registered? <Link to="/login">Sign in</Link></p>
            <button className="button" type="submit" disabled={busy}>
              {busy ? "Creating..." : "Create Account →"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
