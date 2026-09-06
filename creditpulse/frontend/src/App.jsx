import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import CreditRequest from "./pages/CreditRequest";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import ProfileForm from "./pages/ProfileForm";
import Result from "./pages/Result";
import Signup from "./pages/Signup";

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <Navbar />
      <main className="shell"><Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<ProfileForm />} />
        <Route path="/apply" element={<CreditRequest />} />
        <Route path="/result" element={<Result />} />
      </Routes></main>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/*" element={<ProtectedLayout />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
