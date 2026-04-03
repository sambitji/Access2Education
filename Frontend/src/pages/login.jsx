// frontend/src/pages/Login.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, BookOpen, LogIn } from "lucide-react";
import toast from "react-hot-toast";
import api from "../services/api";
import useAuthStore from "../store/authStore";

export default function Login() {
  const navigate       = useNavigate();
  const { login }      = useAuthStore();
  const [form, setForm]       = useState({ email: "", password: "" });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [errors, setErrors]     = useState({});

  const validate = () => {
    const e = {};
    if (!form.email)    e.email    = "Email zaroori hai";
    if (!form.password) e.password = "Password zaroori hai";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.post("/auth/login", form);
      const { access_token, refresh_token, user } = res.data;
      login(user, access_token, refresh_token);
      toast.success(`Welcome back, ${user.name}!`);
      navigate("/dashboard");
    } catch (err) {
      const msg = err.response?.data?.detail || "Login failed. Dobara try karo.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const InputField = ({ icon, name, type, placeholder, value }) => (
    <div>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">{icon}</span>
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => setForm({ ...form, [name]: e.target.value })}
          className={`w-full bg-gray-800 border ${errors[name] ? "border-red-500" : "border-gray-700"}
                      text-white rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none
                      focus:border-indigo-500 transition placeholder-gray-500`}
        />
        {name === "password" && (
          <button type="button" onClick={() => setShowPass(!showPass)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
            {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
      {errors[name] && <p className="text-red-400 text-xs mt-1">{errors[name]}</p>}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-indigo-400 mb-4">
            <BookOpen size={32} />
            <span className="text-2xl font-bold text-white">EduPlatform</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Wapas aao!</h1>
          <p className="text-gray-400 text-sm mt-1">Apne account mein login karo</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}
          className="bg-gray-900 border border-gray-800 rounded-2xl p-8 space-y-5">

          <InputField icon={<Mail size={16}/>} name="email"
            type="email" placeholder="Email address" value={form.email} />

          <InputField icon={<Lock size={16}/>} name="password"
            type={showPass ? "text" : "password"}
            placeholder="Password" value={form.password} />

          <div className="text-right">
            <Link to="/forgot-password" className="text-indigo-400 text-sm hover:underline">
              Password bhool gaye?
            </Link>
          </div>

          <button type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600
                       hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold
                       py-3 rounded-xl transition">
            {loading ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <><LogIn size={18}/> Login Karo</>
            )}
          </button>

          <p className="text-center text-gray-400 text-sm">
            Account nahi hai?{" "}
            <Link to="/register" className="text-indigo-400 hover:underline font-medium">
              Register karo
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}