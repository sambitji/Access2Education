// frontend/src/pages/Home.jsx
import { Link } from "react-router-dom";
import { BookOpen, Brain, BarChart2, MessageSquare, ArrowRight, CheckCircle } from "lucide-react";
import useAuthStore from "../store/authStore";

export default function Home() {
  const { user } = useAuthStore();

  const features = [
    { icon: <Brain size={28} className="text-indigo-400" />,      title: "AI-Powered Clustering",    desc: "Aptitude test ke baad ML model tumhari learning style detect karta hai" },
    { icon: <BookOpen size={28} className="text-emerald-400" />,  title: "Personalized Content",     desc: "Tumhari style ke hisaab se videos, articles aur exercises recommend hote hain" },
    { icon: <MessageSquare size={28} className="text-violet-400"/>,title: "AI Chatbot",              desc: "Lecture summary aur doubts ke liye AI chatbot 24/7 available hai" },
    { icon: <BarChart2 size={28} className="text-amber-400" />,   title: "Progress Tracking",       desc: "Subject-wise progress dekho aur improvement track karo" },
  ];

  const steps = [
    { step: "01", title: "Register karo",        desc: "Account banao — student ya teacher" },
    { step: "02", title: "Aptitude Test do",      desc: "25 questions — 5 sections — 30 minutes" },
    { step: "03", title: "Style Pata Karo",       desc: "ML model tumhari learning style detect karega" },
    { step: "04", title: "Personalized Seekho",   desc: "Tumhare liye specially curated content milega" },
  ];

  return (
    <div className="bg-gray-950 text-white">

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <span className="inline-block bg-indigo-900/50 text-indigo-300 text-sm px-4 py-1.5 rounded-full mb-6 border border-indigo-700">
          🎓 AI-Powered Personalized Learning
        </span>
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight">
          Apni <span className="text-indigo-400">Learning Style</span> ke<br />
          hisaab se seekho
        </h1>
        <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-10">
          Pehle aptitude test do, phir ML model tumhare liye best content recommend karega.
          Visual learner ho ya conceptual thinker — sab ke liye alag approach.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {user ? (
            <Link to="/dashboard"
              className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700
                         text-white px-8 py-3.5 rounded-xl font-semibold text-lg transition">
              Dashboard pe jao <ArrowRight size={20} />
            </Link>
          ) : (
            <>
              <Link to="/register"
                className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700
                           text-white px-8 py-3.5 rounded-xl font-semibold text-lg transition">
                Abhi Shuru Karo <ArrowRight size={20} />
              </Link>
              <Link to="/login"
                className="flex items-center justify-center gap-2 border border-gray-700
                           hover:border-gray-500 text-gray-300 px-8 py-3.5 rounded-xl font-semibold text-lg transition">
                Login Karo
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-900/50 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-4">Platform Features</h2>
          <p className="text-gray-400 text-center mb-12">Jo cheezein Edu-Platform ko alag banati hain</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-2xl p-6 hover:border-indigo-600 transition">
                <div className="mb-4">{f.icon}</div>
                <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Learning Styles */}
      <section className="py-20 max-w-6xl mx-auto px-6">
        <h2 className="text-3xl font-bold text-center mb-4">4 Learning Styles</h2>
        <p className="text-gray-400 text-center mb-12">ML model in 4 clusters mein se ek assign karta hai</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { emoji:"👁️", title:"Visual Learner",     color:"indigo",  traits:["Videos & Diagrams","Animations","Infographics"] },
            { emoji:"🧠", title:"Conceptual Thinker", color:"violet",  traits:["Deep Theory","Case Studies","Articles"] },
            { emoji:"⚙️", title:"Practice-Based",     color:"emerald", traits:["Coding Exercises","Projects","Hands-on"] },
            { emoji:"📋", title:"Step-by-Step",        color:"amber",   traits:["Structured Notes","Guided Tutorials","Checklists"] },
          ].map((s, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
              <div className="text-4xl mb-3">{s.emoji}</div>
              <h3 className="font-semibold text-lg mb-4">{s.title}</h3>
              <ul className="space-y-2">
                {s.traits.map((t, j) => (
                  <li key={j} className="flex items-center gap-2 text-sm text-gray-400">
                    <CheckCircle size={14} className="text-indigo-400 shrink-0" /> {t}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-gray-900/50 py-20">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Kaise Kaam Karta Hai?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {steps.map((s, i) => (
              <div key={i} className="flex gap-4 bg-gray-800/50 border border-gray-700 rounded-2xl p-6">
                <span className="text-3xl font-extrabold text-indigo-600/40">{s.step}</span>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{s.title}</h3>
                  <p className="text-gray-400 text-sm">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      {!user && (
        <section className="py-20 text-center px-6">
          <h2 className="text-3xl font-bold mb-4">Aaj hi shuru karo!</h2>
          <p className="text-gray-400 mb-8">Free mein register karo aur apni learning style discover karo</p>
          <Link to="/register"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700
                       text-white px-10 py-4 rounded-xl font-semibold text-lg transition">
            Register Karo — Free <ArrowRight size={20} />
          </Link>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500 text-sm">
        <p>© 2024 EduPlatform. Built with ❤️ using React + FastAPI + ML</p>
      </footer>
    </div>
  );
}