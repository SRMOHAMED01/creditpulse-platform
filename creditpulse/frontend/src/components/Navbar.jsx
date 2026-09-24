import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

const navClass = ({ isActive }) => isActive ? "active" : "";

export default function Navbar() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem("creditpulse_token");
    sessionStorage.removeItem("creditpulse_result");
    navigate("/login");
  };

  return (
    <header className="navbar">
      <NavLink className="brand" to="/dashboard" aria-label="CreditPulse dashboard">
        <span className="brand-mark" aria-hidden="true">CP</span>
        <span>CreditPulse</span>
      </NavLink>
      <nav className="nav-links" aria-label="Primary navigation">
        <NavLink className={navClass} to="/dashboard">Overview</NavLink>
        <NavLink className={navClass} to="/profile">Profile</NavLink>
        <NavLink className={navClass} to="/apply">Assessment</NavLink>
      </nav>
      <button className="nav-action" onClick={logout} aria-label="Sign out">
        <span>Sign out</span><i aria-hidden="true">↗</i>
      </button>
    </header>
  );
}
