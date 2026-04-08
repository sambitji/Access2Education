// frontend/src/pages/Progress.jsx
import { useEffect, useState } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import api from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Progress() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/content/progress")
      .then((r) => setData(r.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner fullScreen message="Progress load ho rahi hai..." />;
  if (!data)   return <p className="text-center text-gray-400 py-20">Data nahi mila.</p>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <h1 className="text-3xl font-bold text-white">📈 Meri Progress</h1>

      {/* Overall */}
      <div className="flex items-center gap-8 bg-gray-900 border border-gray-800 rounded-2xl p-8">
        <div className="w-28 h-28 shrink-0">
          <CircularProgressbar
            value={data.overall_percentage}
            text={`${data.overall_percentage}%`}
            styles={buildStyles({
              pathColor:"#6366f1", textColor:"#fff",
              trailColor:"#1f2937", textSize:"20px",
            })}
          />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            {data.total_completed} / {data.total_available}
          </h2>
          <p className="text-gray-400">Content items complete kiye</p>
          {data.learning_style && (
            <p className="text-indigo-400 text-sm mt-2 capitalize">
              Style: {data.learning_style.replace(/_/g," ")}
            </p>
          )}
        </div>
      </div>

      {/* Subject breakdown */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Subject-wise Breakdown</h2>
        <div className="space-y-4">
          {Object.entries(data.subject_breakdown || {}).map(([subj, stats]) => (
            <div key={subj} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex justify-between items-center mb-2">
                <span className="text-white font-medium">{subj}</span>
                <span className="text-gray-400 text-sm">{stats.completed}/{stats.total}</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2.5">
                <div className="bg-indigo-500 h-2.5 rounded-full transition-all"
                     style={{ width:`${stats.percentage}%` }} />
              </div>
              <p className="text-indigo-400 text-xs mt-1.5">{stats.percentage}% complete</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent */}
      {data.recently_completed?.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">🕐 Recently Completed</h2>
          <div className="space-y-3">
            {data.recently_completed.map((item) => (
              <div key={item.content_id}
                className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4
                           flex justify-between items-center">
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