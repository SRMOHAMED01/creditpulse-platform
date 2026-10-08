import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitCreditApplication } from "../api/credit";
import { getApiErrorMessage } from "../api/errors";
import client from "../api/client";

const initial = {
  revenu_mensuel: "4500",
  dettes_actuelles: "900",
  age: "32",
  anciennete_emploi: "5",
  nombre_credits_en_cours: "1",
  historique_paiement: "0.95",
  requested_amount: "15000",
  duration_months: "36"
};

export default function CreditRequest() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [profileError, setProfileError] = useState(false);
  const [profileAttempt, setProfileAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setLoadingProfile(true);
    setProfileError(false);
    client.get('/users/profile').then(({ data }) => {
      if (active) setForm((previous) => ({
        ...previous,
        ...Object.fromEntries(Object.keys(initial).filter((key) => key in data).map((key) => [key, String(data[key])])),
      }));
    }).catch((failure) => {
      if (active && failure.response?.status !== 404) setProfileError(true);
    }).finally(() => { if (active) setLoadingProfile(false); });
    return () => { active = false; };
  }, [profileAttempt]);

  const update = (key, value) => setForm({ ...form, [key]: value });

  // Calculate live DTI
  const revenu = Number(form.revenu_mensuel) || 1;
  const dettes = Number(form.dettes_actuelles) || 0;
  const liveDTI = ((dettes / revenu) * 100).toFixed(1);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([key, value]) => [key, Number(value)])
      );
      const { data } = await submitCreditApplication(payload);
      navigate(`/result/${data.id}`);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The scoring service is unavailable. Try again shortly."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="form-page shell">
      <div className="form-header">
        <div className="eyebrow">⚡ Step 02 / Risk Scoring</div>
        <h1>Credit Risk Assessment</h1>
        <p>Adjust your financial parameters to simulate instant ML credit risk scoring.</p>
      </div>

      <div className="assessment-layout">
        <form className="form-card" onSubmit={submit}>
          {loadingProfile && <p role="status">Loading your saved financial profile...</p>}
          {profileError && <p className="error">Could not load your saved profile. <button type="button" className="button secondary" onClick={() => setProfileAttempt((value) => value + 1)}>Retry</button></p>}
          <fieldset disabled={loadingProfile || profileError || busy} style={{ border: 0, padding: 0, margin: 0, minWidth: 0 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Income Slider */}
            <div className="range-slider-field">
              <div className="range-slider-header">
                <label htmlFor="assessment-income">Monthly Income ($)</label>
                <span className="range-slider-value">${Number(form.revenu_mensuel).toLocaleString()}</span>
              </div>
              <input
                id="assessment-income"
                type="range"
                min="1"
                max={Math.max(25000, Number(form.revenu_mensuel) || 0)}
                step="0.01"
                value={form.revenu_mensuel}
                onChange={(e) => update("revenu_mensuel", e.target.value)}
              />
            </div>

            {/* Debt Slider */}
            <div className="range-slider-field">
              <div className="range-slider-header">
                <label htmlFor="assessment-debt">Current Debt ($)</label>
                <span className="range-slider-value">${Number(form.dettes_actuelles).toLocaleString()}</span>
              </div>
              <input
                id="assessment-debt"
                type="range"
                min="0"
                max={Math.max(15000, Number(form.dettes_actuelles) || 0)}
                step="0.01"
                value={form.dettes_actuelles}
                onChange={(e) => update("dettes_actuelles", e.target.value)}
              />
            </div>

            {/* Inputs Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label htmlFor="assessment-age">Age</label>
                <input id="assessment-age" type="number" min="19" max="100" value={form.age} onChange={(e) => update("age", e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="assessment-employment">Employment Seniority (Years)</label>
                <input id="assessment-employment" type="number" min="0" step="0.01" value={form.anciennete_emploi} onChange={(e) => update("anciennete_emploi", e.target.value)} required />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label htmlFor="assessment-credits">Active Credit Lines</label>
                <input id="assessment-credits" type="number" min="0" value={form.nombre_credits_en_cours} onChange={(e) => update("nombre_credits_en_cours", e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="assessment-payment-history">Payment History (0.0 to 1.0)</label>
                <input id="assessment-payment-history" type="number" step="0.01" min="0" max="1" value={form.historique_paiement} onChange={(e) => update("historique_paiement", e.target.value)} required />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label htmlFor="assessment-amount">Requested Amount ($)</label>
                <input id="assessment-amount" type="number" min="0.01" step="0.01" value={form.requested_amount} onChange={(e) => update("requested_amount", e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="assessment-duration">Duration (Months)</label>
                <input id="assessment-duration" type="number" min="1" max="360" value={form.duration_months} onChange={(e) => update("duration_months", e.target.value)} required />
              </div>
            </div>

          </div>
          </fieldset>

          {error && <div className="error">{error}</div>}

          <div style={{ marginTop: '28px', textAlign: 'right' }}>
            <button className="button" type="submit" disabled={busy || loadingProfile || profileError} style={{ width: '100%', minHeight: '52px' }}>
              {busy ? "Evaluating ML Model..." : "Run Risk Evaluation →"}
            </button>
          </div>
        </form>

        {/* Live Feature Preview Panel */}
        <aside className="form-card" style={{ background: 'var(--gradient-card)', borderColor: 'var(--border-purple)' }}>
          <div className="eyebrow">📈 Live Feature Store Signals</div>
          <h3 style={{ margin: '10px 0 20px' }}>Derived Metrics</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Debt-to-Income (DTI) Ratio</div>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: liveDTI > 40 ? '#F87171' : '#34D399', fontFamily: 'Space Grotesk' }}>
                {liveDTI}%
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                {liveDTI > 40 ? '⚠️ High DTI may increase risk score' : '✅ Optimal DTI range (< 40%)'}
              </div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Estimated Monthly Payment</div>
              <div style={{ fontSize: '1.6rem', fontWeight: '700', color: '#FFF', fontFamily: 'Space Grotesk' }}>
                ${(Number(form.requested_amount) / (Number(form.duration_months) || 1)).toFixed(0)} / mo
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
