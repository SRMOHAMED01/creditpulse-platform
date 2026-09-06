import React from "react";
import { Link } from "react-router-dom";
import ScoreGauge from "../components/ScoreGauge";
import ShapChart from "../components/ShapChart";

export default function Result() {
  const result = JSON.parse(sessionStorage.getItem("creditpulse_result") || "null");
  if (!result) return <section className="form-page"><div className="panel"><div className="eyebrow">No assessment yet</div><h2>Your next signal is waiting.</h2><p>Submit a credit request to see a score and an explanation.</p><Link className="button" to="/apply">Start a request</Link></div></section>;
  return <section><div className="form-header"><div className="eyebrow">Assessment complete</div><h2>Here is what the model sees.</h2><p>This is a decision aid, not a promise of approval. The explanation keeps the result readable.</p></div><div className="result-grid"><div className="result-score"><div><span>CreditPulse score</span><ScoreGauge score={result.score} /><div>{result.decision}</div></div></div><div className="panel"><h3>Risk signals</h3><div className="explanation"><span>Estimated default probability</span><strong>{Math.round(result.probability_default * 100)}%</strong></div><ShapChart values={result.explanation} /><Link className="button secondary" to="/apply">Run another assessment</Link></div></div></section>;
}
