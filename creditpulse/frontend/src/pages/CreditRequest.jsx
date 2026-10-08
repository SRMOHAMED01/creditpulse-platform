import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitCreditApplication } from "../api/credit";
import { getApiErrorMessage } from "../api/errors";

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

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px' }}>
        <form className="form-card" onSubmit={submit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Income Slider */}
            <div className="range-slider-field">
              <div className="range-slider-header">
                <span>Monthly Income ($)</span>
                <span className="range-slider-value">${Number(form.revenu_mensuel).toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="1000"
                max="25000"
                step="250"
                value={form.revenu_mensuel}
                onChange={(e) => update("revenu_mensuel", e.target.value)}
              />
            </div>

            {/* Debt Slider */}
            <div className="range-slider-field">
              <div className="range-slider-header">
                <span>Current Debt ($)</span>
                <span className="range-slider-value">${Number(form.dettes_actuelles).toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="0"
                max="15000"
                step="100"
                value={form.dettes_actuelles}
                onChange={(e) => update("dettes_actuelles", e.target.value)}
              />
            </div>

            {/* Inputs Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label>Age</label>
                <input type="number" min="18" max="100" value={form.age} onChange={(e) => update("age", e.target.value)} required />
              </div>
              <div className="field">
                <label>Employment Seniority (Years)</label>
                <input type="number" min="0" max="50" value={form.anciennete_emploi} onChange={(e) => update("anciennete_emploi", e.target.value)} required />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label>Active Credit Lines</label>
                <input type="number" min="0" max="20" value={form.nombre_credits_en_cours} onChange={(e) => update("nombre_credits_en_cours", e.target.value)} required />
              </div>
              <div className="field">
                <label>Payment History (0.0 to 1.0)</label>
                <input type="number" step="0.01" min="0" max="1" value={form.historique_paiement} onChange={(e) => update("historique_paiement", e.target.value)} required />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="field">
                <label>Requested Amount ($)</label>
                <input type="number" min="500" value={form.requested_amount} onChange={(e) => update("requested_amount", e.target.value)} required />
              </div>
              <div className="field">
                <label>Duration (Months)</label>
                <input type="number" min="6" max="120" value={form.duration_months} onChange={(e) => update("duration_months", e.target.value)} required />
              </div>
            </div>

          </div>

          {error && <div className="error">{error}</div>}

          <div style={{ marginTop: '28px', textAlign: 'right' }}>
            <button className="button" type="submit" disabled={busy} style={{ width: '100%', minHeight: '52px' }}>
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
