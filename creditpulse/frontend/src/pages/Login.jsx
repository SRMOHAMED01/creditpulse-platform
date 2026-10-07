import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import { getApiErrorMessage } from "../api/errors";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { data } = await login(form);
      localStorage.setItem("creditpulse_token", data.access_token);
      navigate(location.state?.from || "/dashboard");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to sign in. Check your credentials."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-hero">
        <div className="eyebrow">✨ Next-Gen Credit Scoring</div>
        <h1>Intelligent Risk Assessment, <span>Amplified.</span></h1>
        <p>Sign in to access your financial workspace, monitor real-time credit metrics, and explore transparent AI decisions.</p>
        
        <div className="auth-features">
          <div className="feature-pill">
            <span className="feature-pill-icon">⚡</span>
            <span>Real-time XGBoost ML Risk Engine</span>
          </div>
          <div className="feature-pill">
            <span className="feature-pill-icon">🔍</span>
            <span>Granular SHAP Feature Explainability</span>
          </div>
          <div className="feature-pill">
            <span className="feature-pill-icon">🛡️</span>
            <span>Bank-grade Encrypted Data Pipeline</span>
          </div>
        </div>
      </div>

      <div className="auth-card">
        <div className="form-header">
          <div className="eyebrow">Secure Access</div>
          <h2>Welcome Back</h2>
          <p>Enter your credentials to continue</p>
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
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                required
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
          </div>

          {error && <div className="error">{error}</div>}

          <div className="form-footer">
            <p>New to CreditPulse? <Link to="/signup">Create account</Link></p>
            <button className="button" type="submit" disabled={busy}>
              {busy ? "Signing in..." : "Sign In →"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
