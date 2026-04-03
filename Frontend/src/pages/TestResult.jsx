// frontend/src/pages/TestResult.jsx — FIXED VERSION
// Added: confidence score, correct_answers, total_marks display
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";
import { BookOpen, ArrowRight, RefreshCw, CheckCircle, Target } from "lucide-react";
import api from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";

const STYLE_CONFIG = {
  visual_learner:     { emoji:"👁️", label:"Visual Learner",    bg:"from-indigo-900/40",  border:"border-indigo-700/50" },
  conceptual_thinker: { emoji:"🧠", label:"Conceptual Thinker",bg:"from-violet-900/40",  border:"border-violet-700/50" },
  practice_based:     { emoji:"⚙️", label:"Practice-Based",   bg:"from-emerald-900/40", border:"border-emerald-700/50"},
  step_by_step:       { emoji:"📋", label:"Step-by-Step",      bg:"from-amber-900/40",   border:"border-amber-700/50"  },
};

export default function TestResult() {
  const navigate            = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/test/result")
      .then((r) => setResult(r.data))
      .catch(() => navigate("/test"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner fullScreen message="Result load ho raha hai..." />;
  if (!result)  return null;

  const { scores, learning_style, style_details,
          days_until_retake, can_retake,
          confidence, correct_answers, total_marks, out_of, ml_mode } = result;

  const cfg = STYLE_CONFIG[learning_style] || STYLE_CONFIG.visual_learner;

  const radarData = [
    { subject:"Logical",   score: scores.logical },
    { subject:"Verbal",    score: scores.verbal },
    { subject:"Numerical", score: scores.numerical },
    { subject:"Memory",    score: scores.memory },
    { subject:"Attention", score: scores.attention },
  ];

  const perfLabel = scores.total >= 80 ? "Excellent 🌟"
                  : scores.total >= 60 ? "Good 👍"
                  : scores.total >= 40 ? "Average 📊"
                  : "Needs Improvement 💪";

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">

      {/* Hero */}
      <div className={`bg-gradient-to-br ${cfg.bg} to-gray-900 border ${cfg.border}
                       rounded-2xl p-8 text-center`}>
        <div className="text-6xl mb-3">{cfg.emoji}</div>
        <p className="text-gray-400 text-sm mb-1">Tumhara Learning Style</p>
        <h1 className="text-3xl font-extrabold text-white mb-2">{cfg.label}</h1>
        <p className="text-gray-300 text-sm max-w-md mx-auto">{style_details?.description}</p>

        {/* Score stats */}
        <div className="grid grid-cols-3 gap-3 mt-6">
          <div className="bg-gray-900/60 border border-gray-700 rounded-xl p-3">
            <p className="text-2xl font-bold text-indigo-400">{scores.total}%</p>
            <p className="text-gray-400 text-xs mt-0.5">Overall Score</p>
          </div>
          <div className="bg-gray-900/60 border border-gray-700 rounded-xl p-3">
            <p className="text-2xl font-bold text-emerald-400">{correct_answers || 0}/25</p>
            <p className="text-gray-400 text-xs mt-0.5">Correct Answers</p>
          </div>
          <div className="bg-gray-900/60 border border-gray-700 rounded-xl p-3">
            <p className="text-2xl font-bold text-amber-400">{total_marks || 0}/{out_of || 500}</p>
            <p className="text-gray-400 text-xs mt-0.5">Total Marks</p>
          </div>
        </div>

        {/* Confidence + Performance */}
        <div className="flex items-center justify-center gap-4 mt-4">
          {confidence && (
            <span className="flex items-center gap-1.5 text-sm bg-gray-900/60
                             border border-gray-700 px-3 py-1.5 rounded-full">
              <Target size={13} className="text-indigo-400"/>
              <span className="text-gray-300">Model Confidence: </span>
              <span className="text-indigo-300 font-semibold">{(confidence * 100).toFixed(1)}%</span>
            </span>
          )}
          <span className="text-sm text-gray-300">{perfLabel}</span>
        </div>

        {ml_mode && (
          <p className="text-xs text-gray-600 mt-2">
            Predicted by: {ml_mode === "ensemble" ? "🤖 AI Ensemble Model" : "📏 Rule-Based"}
          </p>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Radar */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-4 text-center text-sm">Score Radar</h2>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="subject" tick={{ fill:"#9ca3af", fontSize:10 }} />
              <Tooltip contentStyle={{ background:"#1f2937", border:"none", borderRadius:8 }}
                       itemStyle={{ color:"#818cf8" }} />
              <Radar dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Bars */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-4 text-sm">Section Scores</h2>
          <div className="space-y-3">
            {radarData.map((item) => (
              <div key={item.subject}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">{item.subject}</span>
                  <span className="text-white font-medium">{item.score}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div className="bg-indigo-500 h-2 rounded-full transition-all"
                       style={{ width:`${item.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strengths + Content Types */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-3 text-sm">💪 Tumhari Strengths</h2>
          <ul className="space-y-2">
            {style_details?.strengths?.map((s, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle size={13} className="text-emerald-400 shrink-0"/> {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-3 text-sm">🎯 Best Content Types</h2>
          <div className="flex flex-wrap gap-2 mb-3">
            {style_details?.content_types?.map((ct, i) => (
              <span key={i} className="bg-indigo-900/40 border border-indigo-700
                                        text-indigo-300 text-xs px-3 py-1 rounded-full">{ct}</span>
            ))}
          </div>
          {style_details?.study_tip && (
            <div className="bg-amber-900/20 border border-amber-700/40 rounded-xl p-3">
              <p className="text-amber-300 text-xs">💡 {style_details.study_tip}</p>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button onClick={() => navigate("/dashboard")}
          className="flex-1 flex items-center justify-center gap-2 bg-indigo-600
                     hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl transition">
          <BookOpen size={18}/> Dashboard
        </button>
        <button onClick={() => navigate("/learn")}
          className="flex-1 flex items-center justify-center gap-2 bg-gray-800
                     hover:bg-gray-700 text-white font-semibold py-3.5 rounded-xl transition">
          Seekhna Shuru Karo <ArrowRight size={18}/>
        </button>
      </div>

      {!can_retake && (
        <p className="text-center text-gray-500 text-xs">
          <RefreshCw size={11} className="inline mr-1"/>
          Dobara test {days_until_retake} din baad de sakte ho
        </p>
      )}
    </div>
  );
}