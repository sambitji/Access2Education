// frontend/src/components/Dashboard/ProgressChart.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const COLORS = ["#6366f1","#8b5cf6","#10b981","#f59e0b","#ef4444","#06b6d4"];

export default function ProgressChart({ subjectBreakdown }) {
  if (!subjectBreakdown) return null;

  const data = Object.entries(subjectBreakdown).map(([subject, stats]) => ({
    subject: subject.length > 8 ? subject.slice(0,7)+"…" : subject,
    fullName: subject,
    completed: stats.completed,
    total:     stats.total,
    pct:       stats.percentage,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm">
        <p className="text-white font-semibold mb-1">{d.fullName}</p>
        <p className="text-indigo-400">{d.completed}/{d.total} completed</p>
        <p className="text-gray-400">{d.pct}%</p>
      </div>
    );
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <h2 className="text-white font-semibold mb-6">📊 Subject-wise Progress</h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barCategoryGap="30%">
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="subject" tick={{ fill:"#9ca3af", fontSize:12 }} axisLine={false} tickLine={false} />
          <YAxis domain={[0,100]} tickFormatter={(v) => v+"%"}
                 tick={{ fill:"#9ca3af", fontSize:11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill:"rgba(99,102,241,0.05)" }} />
          <Bar dataKey="pct" radius={[6,6,0,0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}