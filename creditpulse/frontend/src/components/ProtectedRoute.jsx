/*
ProtectedRoute.jsx — Composant ProtectedRoute (Palier A.3)


*/
import React from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  if (!localStorage.getItem("creditpulse_token")) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}
