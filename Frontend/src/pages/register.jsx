// frontend/src/pages/Register.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User, Mail, Lock, Eye, EyeOff, BookOpen, UserPlus } from "lucide-react";
import toast from "react-hot-toast";
import api from "../services/api";
import useAuthStore from "../store/authStore";

export default function Register() {
  const navigate  = useNavigate();
  const { login } = useAuthStore();
  const [form, setForm]         = useState({ name:"", email:"", password:"", role:"student" });
  const [showPass, setShowPass]  = useState(false);
  const [loading, setLoading]    = useState(false);
  const [errors, setErrors]      = useState({});

  const validate = () => {
    const e = {};
    if (!form.name || form.name.length < 2) e.name = "Naam kam se kam 2 characters ka hona chahiye";
    if (!form.email)    e.email    = "Email zaroori hai";
    if (!form.password || form.password.length < 8) e.password = "Password minimum 8 characters";
    if (!/[A-Z]/.test(form.password)) e.password = "Ek uppercase letter zaroori hai";
    if (!/[0-9]/.test(form.password)) e.password = "Ek digit zaroori hai";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.post("/auth/register", form);
      const { access_token, refresh_token, user } = res.data;
      login(user, access_token, refresh_token);
      toast.success(`Welcome, ${user.name}! 🎉`);
      navigate("/test");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-indigo-400 mb-4">
            <BookOpen size={32} />
            <span className="text-2xl font-bold text-white">EduPlatform</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Account Banao</h1>
          <p className="text-gray-400 text-sm mt-1">Aaj se personalized learning shuru karo</p>
        </div>

        <form onSubmit={handleSubmit}
          className="bg-gray-900 border border-gray-800 rounded-2xl p-8 space-y-5">

          {/* Name */}
          <div>
            <div className="relative">
              <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input type="text" placeholder="Poora naam"
                value={form.name}
                onChange={(e) => setForm({...form, name: e.target.value})}
                className={`w-full bg-gray-800 border ${errors.name?"border-red-500":"border-gray-700"}
                            text-white rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none
                            focus:border-indigo-500 transition placeholder-gray-500`} />
            </div>
            {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name}</p>}
          </div>

          {/* Email */}
          <div>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input type="email" placeholder="Email address"
                value={form.email}
                onChange={(e) => setForm({...form, email: e.target.value})}
                className={`w-full bg-gray-800 border ${errors.email?"border-red-500":"border-gray-700"}
                            text-white rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none
                            focus:border-indigo-500 transition placeholder-gray-500`} />
            </div>
            {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
          </div>

          {/* Password */}
          <div>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input type={showPass?"text":"password"} placeholder="Password (min 8 chars)"
                value={form.password}
                onChange={(e) => setForm({...form, password: e.target.value})}
                className={`w-full bg-gray-800 border ${errors.password?"border-red-500":"border-gray-700"}
                            text-white rounded-xl pl-10 pr-10 py-3 text-sm focus:outline-none
                            focus:border-indigo-500 transition placeholder-gray-500`} />
              <button type="button" onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                {showPass ? <EyeOff size={16}/> : <Eye size={16}/>}
              </button>
            </div>
            {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
          </div>

          {/* Role */}
          <div>
            <label className="text-gray-400 text-sm block mb-2">Aap kaun hain?</label>
            <div className="grid grid-cols-2 gap-3">
              {["student","teacher"].map((r) => (
                <button key={r} type="button"
                  onClick={() => setForm({...form, role: r})}
                  className={`py-2.5 rounded-xl text-sm font-medium capitalize border transition
                              ${form.role===r
                                ? "bg-indigo-600 border-indigo-600 text-white"
                                : "bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500"}`}>
                  {r === "student" ? "🎓 Student" : "👨‍🏫 Teacher"}
                </button>
              ))}
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600
                       hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold
                       py-3 rounded-xl transition">
            {loading
              ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              : <><UserPlus size={18}/> Register Karo</>}
          </button>

          <p className="text-center text-gray-400 text-sm">
            Already account hai?{" "}
            <Link to="/login" className="text-indigo-400 hover:underline font-medium">Login karo</Link>
          </p>
        </form>
      </div>
    </div>
  );
}