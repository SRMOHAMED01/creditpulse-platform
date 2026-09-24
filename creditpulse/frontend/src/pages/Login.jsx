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
    event.preventDefault(); setBusy(true); setError("");
    try { const { data } = await login(form); localStorage.setItem("creditpulse_token", data.access_token); navigate(location.state?.from || "/dashboard"); }
    catch (requestError) { setError(getApiErrorMessage(requestError, "Unable to sign in. Check your credentials.")); }
    finally { setBusy(false); }
  };
  return <section className="form-page"><div className="form-header"><div className="eyebrow">CreditPulse / secure access</div><h1>Make the next financial move with clarity.</h1><p>Sign in to see your profile and continue an application.</p></div><form className="form-card" onSubmit={submit}><div className="field-grid"><Field label="Email" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} /><Field label="Password" type="password" value={form.password} onChange={(value) => setForm({ ...form, password: value })} /></div>{error && <div className="error">{error}</div>}<div className="form-footer"><p>New to CreditPulse? <Link to="/signup">Create an account</Link></p><button className="button" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button></div></form></section>;
}

function Field({ label, type, value, onChange }) { const id = `login-${type}`; return <div className="field full"><label htmlFor={id}>{label}</label><input id={id} name={type} autoComplete={type === "password" ? "current-password" : "email"} required type={type} value={value} onChange={(event) => onChange(event.target.value)} /></div>; }
