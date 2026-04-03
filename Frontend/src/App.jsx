// =============================================================
// frontend/src/App.jsx
// Edu-Platform — Main Application Router
//
// Routes:
//   /                    -> Home page (public)
//   /login               -> Login page (public)
//   /register            -> Register page (public)
//   /test                -> Aptitude test (protected - student)
//   /test/result         -> Test result (protected - student)
//   /dashboard           -> Student dashboard (protected - student)
//   /learn               -> Learning page (protected - student)
//   /learn/:contentId    -> Single content detail (protected)
//   /progress            -> Progress page (protected - student)
//   *                    -> 404 Not Found
// =============================================================

import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { Toaster } from "react-hot-toast";

// ── Pages ──────────────────────────────────────────────────────
import Home          from "./pages/Home";
import Login         from "./pages/Login";
import Register      from "./pages/Register";
import TestPage      from "./pages/TestPage";
import TestResult    from "./pages/TestResult";
import LearnPage     from "./pages/LearnPage";
import Dashboard     from "./pages/Dashboard";
import Progress      from "./pages/Progress";
import NotFound      from "./pages/NotFound";

// ── Components ─────────────────────────────────────────────────
import Navbar        from "./components/Navbar";
import LoadingSpinner from "./components/LoadingSpinner";

// ── Store ──────────────────────────────────────────────────────
import useAuthStore  from "./store/authStore";


// =============================================================
// Protected Route — Login nahi kiya toh /login pe redirect
// =============================================================

function ProtectedRoute({ allowedRoles = [] }) {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return <LoadingSpinner fullScreen message="Loading..." />;
  }

  // Login nahi hai toh login page pe bhejo
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Role check — agar allowedRoles specify ki hain
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}


// =============================================================
// Public Route — Already logged in toh dashboard pe bhejo
// =============================================================

function PublicRoute() {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return <LoadingSpinner fullScreen message="Loading..." />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}


// =============================================================
// Layout — Navbar ke saath
// =============================================================

function WithNavbar() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gray-50 pt-16">
        <Outlet />
      </main>
    </>
  );
}


// =============================================================
// App Root
// =============================================================

export default function App() {
  const { initAuth, isLoading } = useAuthStore();

  // App start hone pe localStorage se user restore karo
  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (isLoading) {
    return <LoadingSpinner fullScreen message="Edu-Platform load ho raha hai..." />;
  }

  return (
    <BrowserRouter>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#1f2937",
            color:      "#f9fafb",
            fontSize:   "14px",
          },
          success: { iconTheme: { primary: "#10b981", secondary: "#f9fafb" } },
          error:   { iconTheme: { primary: "#ef4444", secondary: "#f9fafb" } },
        }}
      />

      <Routes>

        {/* ── Public Routes (login/register) ────────────────── */}
        <Route element={<PublicRoute />}>
          <Route path="/login"    element={<Login    />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* ── Routes with Navbar ────────────────────────────── */}
        <Route element={<WithNavbar />}>

          {/* Home — sabke liye */}
          <Route path="/" element={<Home />} />

          {/* ── Protected — Students only ─────────────────── */}
          <Route element={<ProtectedRoute allowedRoles={["student"]} />}>
            <Route path="/test"        element={<TestPage   />} />
            <Route path="/test/result" element={<TestResult />} />
            <Route path="/dashboard"   element={<Dashboard  />} />
            <Route path="/learn"       element={<LearnPage  />} />
            <Route path="/learn/:contentId" element={<LearnPage />} />
            <Route path="/progress"    element={<Progress   />} />
          </Route>

        </Route>

        {/* ── 404 ───────────────────────────────────────────── */}
        <Route path="*" element={<NotFound />} />

      </Routes>
    </BrowserRouter>
  );
}