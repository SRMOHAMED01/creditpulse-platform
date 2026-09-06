import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

const initial = { revenu_mensuel: "", dettes_actuelles: "", age: "", anciennete_emploi: "", nombre_credits_en_cours: "", historique_paiement: "" };
export default function ProfileForm() {
  const navigate = useNavigate(); const [form, setForm] = useState(initial); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  useEffect(() => { client.get("/users/profile").then(({ data }) => setForm(data)).catch(() => {}); }, []);
  const update = (key, value) => setForm({ ...form, [key]: value });
  const submit = async (event) => { event.preventDefault(); setMessage(""); setError(""); try { await client.post("/users/profile", Object.fromEntries(Object.entries(form).map(([key, value]) => [key, Number(value)]))); setMessage("Profile saved. You can now request a score."); } catch (requestError) { setError(requestError.response?.data?.detail || "Please check every field."); } };
  return <section className="form-page"><div className="form-header"><div className="eyebrow">Step 01 / profile</div><h2>Give your finances a useful shape.</h2><p>Use monthly values and a payment history score between 0 and 1.</p></div><form className="form-card" onSubmit={submit}><div className="field-grid"><Field label="Monthly income" value={form.revenu_mensuel} onChange={(v) => update("revenu_mensuel", v)} /><Field label="Current debt" value={form.dettes_actuelles} onChange={(v) => update("dettes_actuelles", v)} /><Field label="Age" value={form.age} onChange={(v) => update("age", v)} /><Field label="Years in current job" value={form.anciennete_emploi} onChange={(v) => update("anciennete_emploi", v)} /><Field label="Open credit accounts" value={form.nombre_credits_en_cours} onChange={(v) => update("nombre_credits_en_cours", v)} /><Field label="Payment history (0 to 1)" step="0.01" value={form.historique_paiement} onChange={(v) => update("historique_paiement", v)} /></div>{message && <div className="success">{message}</div>}{error && <div className="error">{error}</div>}<div className="form-footer"><span /> <button className="button">Save profile</button></div></form></section>;
}

function Field({ label, value, onChange, step = "1" }) { return <div className="field"><label>{label}</label><input required type="number" min="0" step={step} value={value} onChange={(event) => onChange(event.target.value)} /></div>; }
