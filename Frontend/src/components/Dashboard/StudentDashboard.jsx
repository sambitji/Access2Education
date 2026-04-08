// frontend/src/components/Dashboard/StudentDashboard.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BookOpen, BarChart2, ClipboardList, TrendingUp, ArrowRight, Lock } from "lucide-react";
import api from "../../services/api";
import useAuthStore from "../../store/authStore";
import ProgressChart from "./ProgressChart";
import LoadingSpinner from "../LoadingSpinner";

const STYLE_CONFIG = {
  visual_learner:     { emoji:"👁️", label:"Visual Learner",    color:"indigo" },
  conceptual_thinker: { emoji:"🧠", label:"Conceptual Thinker", color:"violet" },
  practice_based:     { emoji:"⚙️", label:"Practice-Based",    color:"emerald"},
  step_by_step:       { emoji:"📋", label:"Step-by-Step",       color:"amber"  },
};

export default function StudentDashboard() {
  const navigate        = useNavigate();
  const { user }        = useAuthStore();
  const [recs, setRecs]         = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/content/recommendations?top_n=6").catch(() => ({ data: { recommendations:[] } })),
      api.get("/content/progress").catch(() => ({ data: null })),
    ]).then(([recRes, progRes]) => {
      setRecs(recRes.data.recommendations || []);
      setProgress(progRes.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Dashboard load ho raha hai..." />;

  const cfg = STYLE_CONFIG[user?.learning_style];

  const TYPE_ICON = {
    video:"🎥", article:"📄", exercise:"💻", notes:"📋",
    infographic:"🖼️", tutorial:"📖", project:"🚀",
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">

      {/* Welcome */}
      <div className="bg-gradient-to-r from-indigo-900/40 to-gray-900 border border-indigo-700/30
                      rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center
                      justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Namaste, {user?.name?.split(" ")[0]}! 👋
          </h1>
          {cfg ? (
            <p className="text-gray-400 text-sm">
              Tumhara style: <span className="text-indigo-300 font-medium">{cfg.emoji} {cfg.label}</span>
            </p>
          ) : (
            <p className="text-amber-400 text-sm">⚠️ Pehle aptitude test do!</p>
          )}
        </div>
        {!user?.learning_style && (
          <button onClick={() => navigate("/test")}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white
                       px-5 py-2.5 rounded-xl text-sm font-medium transition">
            Test Do <ArrowRight size={16}/>
          </button>
        )}
      </div>

      {/* Stats */}
      {progress && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label:"Completed",      value: progress.total_completed,              icon:<BookOpen size={20}/>,    color:"indigo" },
            { label:"Overall %",      value: progress.overall_percentage + "%",     icon:<TrendingUp size={20}/>,  color:"emerald"},
            { label:"Available",      value: progress.total_available,              icon:<ClipboardList size={20}/>,color:"violet"},
            { label:"Subjects",       value: Object.keys(progress.subject_breakdown||{}).length, icon:<BarChart2 size={20}/>, color:"amber"},
          ].map((s, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <div className="text-gray-500 mb-3">{s.icon}</div>
              <p className="text-2xl font-bold text-white">{s.value}</p>
              <p className="text-gray-400 text-xs mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Progress Chart */}
      {progress && <ProgressChart subjectBreakdown={progress.subject_breakdown} />}

      {/* Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold text-white">🎯 Tumhare Liye Recommendations</h2>
          <button onClick={() => navigate("/learn")}
            className="text-indigo-400 hover:text-indigo-300 text-sm flex items-center gap-1">
            Sab dekho <ArrowRight size={14}/>
          </button>
        </div>

        {!user?.learning_style ? (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-10 text-center">
            <Lock size={40} className="text-gray-600 mx-auto mb-3" />
            <p className="text-white font-semibold mb-1">Recommendations Locked</p>
            <p className="text-gray-400 text-sm mb-4">Aptitude test do — phir personalized content milega</p>
            <button onClick={() => navigate("/test")}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl text-sm transition">
              Test Shuru Karo
            </button>
          </div>
        ) : recs.length === 0 ? (
          <p className="text-gray-400 text-center py-10">
            Sab content complete ho gaya! 🎉 Naye content jald aayenge.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recs.map((item) => (
              <div key={item.content_id}
                onClick={() => navigate(`/learn/${item.content_id}`)}
                className="bg-gray-900 border border-gray-800 hover:border-indigo-600/50
                           rounded-2xl p-5 cursor-pointer transition group">
                <div className="flex items-start justify-between mb-3">
                  <span className="text-2xl">{TYPE_ICON[item.type] || "📚"}</span>
                  <div className="flex items-center gap-2">
                    <span className="bg-gray-800 text-gray-400 text-xs px-2 py-0.5 rounded-full capitalize">
                      {item.type}
                    </span>
                    <span className="text-yellow-500 text-xs">{"★".repeat(item.difficulty)}</span>
                  </div>
                </div>
                <h3 className="text-white font-medium text-sm mb-2 group-hover:text-indigo-300 transition leading-snug">
                  {item.title}
                </h3>
                <p className="text-gray-500 text-xs mb-3 line-clamp-2">{item.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{item.subject}</span>
                  <span>{item.duration_min} min</span>
                </div>
                {!item.prerequisites_met && (
                  <div className="mt-2 text-xs text-amber-400 flex items-center gap-1">
                    <Lock size={10}/> Prerequisites baaki hain
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent */}
      {progress?.recently_completed?.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-white mb-4">✅ Recently Completed</h2>
          <div className="space-y-2">
            {progress.recently_completed.map((item) => (
              <div key={item.content_id}
                className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-3
                           flex items-center justify-between">
                <div>
                  <p className="text-white text-sm font-medium">{item.title}</p>
                  <p className="text-gray-500 text-xs">{item.subject}</p>
                </div>
                <span className="text-gray-500 text-xs">
                  {new Date(item.completed_at).toLocaleDateString("en-IN")}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}