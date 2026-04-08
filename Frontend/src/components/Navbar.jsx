import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-slate-800/70 bg-slate-950/95 backdrop-blur-lg">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="text-lg font-semibold text-white">
          Access2Education
        </Link>

        <nav className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
          <Link to="/" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
            Home
          </Link>
          {user ? (
            <>
              <Link to="/dashboard" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
                Dashboard
              </Link>
              <Link to="/learn" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
                Learn
              </Link>
              <Link to="/progress" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
                Progress
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-xl bg-indigo-600 px-3 py-2 text-white hover:bg-indigo-500 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
                Login
              </Link>
              <Link to="/register" className="rounded-xl px-3 py-2 hover:bg-slate-800 hover:text-white transition">
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
