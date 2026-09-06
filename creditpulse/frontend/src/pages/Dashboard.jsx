import React from "react";
import { Link } from "react-router-dom";

export default function Dashboard() {
  return <><section className="dashboard-head"><div><div className="eyebrow">Your credit workspace</div><h1>A calmer way to make a credit decision.</h1><p>Complete your profile once, then use it to understand each new request.</p></div><Link className="button" to="/apply">Start a request</Link></section><section className="stats"><div className="stat"><span>Profile status</span><strong>Ready to build</strong></div><div className="stat"><span>Last assessment</span><strong>Not yet scored</strong></div><div className="stat"><span>Decision style</span><strong>Explainable</strong></div></section><section className="action-row"><Link className="action-card" to="/profile"><div><h2>Build your profile</h2><p>Give the model the context it needs: income, debt, work history and payment habits.</p></div><span>Complete profile →</span></Link><Link className="action-card" to="/apply"><div><h2>Explore an application</h2><p>See a risk score, decision and the signals that shaped it.</p></div><span>Request a score →</span></Link></section></>;
}
