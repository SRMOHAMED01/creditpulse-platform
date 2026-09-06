import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem("creditpulse_token");
    navigate("/login");
  };

  return <header className="navbar">
    <NavLink className="brand" to="/dashboard"><span className="brand-mark">+</span>CreditPulse</NavLink>
    <nav className="nav-links">
      <NavLink className={({ isActive }) => isActive ? "active" : ""} to="/dashboard">Overview</NavLink>
      <NavLink className={({ isActive }) => isActive ? "active" : ""} to="/profile">Profile</NavLink>
      <NavLink className={({ isActive }) => isActive ? "active" : ""} to="/apply">New request</NavLink>
      <button className="nav-action" onClick={logout}>Sign out</button>
    </nav>
  </header>;
}
