import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/auth";
import { getApiErrorMessage } from "../api/errors";

export default function Signup() {
  const navigate = useNavigate(); const [form, setForm] = useState({ email: "", password: "" }); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const submit = async (event) => { event.preventDefault(); setBusy(true); setError(""); try { const { data } = await register(form); localStorage.setItem("creditpulse_token", data.access_token); navigate("/profile"); } catch (requestError) { setError(getApiErrorMessage(requestError, "Unable to create your account.")); } finally { setBusy(false); } };
  return <section className="form-page"><div className="form-header"><div className="eyebrow">CreditPulse / start here</div><h1>A sharper view of your borrowing power.</h1><p>Create your secure account. Your financial profile stays yours.</p></div><form className="form-card" onSubmit={submit}><div className="field-grid"><Field label="Email" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} /><Field label="Password" type="password" value={form.password} onChange={(value) => setForm({ ...form, password: value })} /></div>{error && <div className="error">{error}</div>}<div className="form-footer"><p>Already registered? <Link to="/login">Sign in</Link></p><button className="button" disabled={busy}>{busy ? "Creating..." : "Create account"}</button></div></form></section>;
}

function Field({ label, type, value, onChange }) { const id = `signup-${type}`; return <div className="field full"><label htmlFor={id}>{label}</label><input id={id} name={type} autoComplete={type === "password" ? "new-password" : "email"} required minLength={type === "password" ? 8 : undefined} type={type} value={value} onChange={(event) => onChange(event.target.value)} /></div>; }
