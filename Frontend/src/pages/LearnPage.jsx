// frontend/src/pages/LearnPage.jsx
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Search, Filter, ArrowLeft } from "lucide-react";
import toast from "react-hot-toast";
import api from "../services/api";
import LecturePlayer from "../components/Lecture/LecturePlayer";
import SummaryPanel  from "../components/Lecture/SummaryPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import useAuthStore   from "../store/authStore";

const SUBJECTS = ["All","Python","DSA","ML","Mathematics","Web Dev","DBMS"];
const TYPES    = ["All","video","article","exercise","notes","infographic","tutorial","project"];
const TYPE_ICON= { video:"🎥",article:"📄",exercise:"💻",notes:"📋",infographic:"🖼️",tutorial:"📖",project:"🚀" };

export default function LearnPage() {
  const { contentId }         = useParams();
  const navigate              = useNavigate();
  const { user }              = useAuthStore();

  // List view state
  const [items, setItems]         = useState([]);
  const [loading, setLoading]     = useState(true);
  const [subject, setSubject]     = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");
  const [search, setSearch]       = useState("");
  const [page, setPage]           = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Detail view state
  const [content, setContent]     = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [isCompleted, setIsCompleted]     = useState(false);
  const [completedIds, setCompletedIds]   = useState([]);

  // ── Load completed IDs once ──────────────────────────────────
  useEffect(() => {
    api.get("/content/progress")
      .then((r) => setCompletedIds(r.data.completed_ids || []))
      .catch(() => {});
  }, []);

  // ── Load content list ────────────────────────────────────────
  useEffect(() => {
    if (contentId) return; // Detail mode — skip list load
    setLoading(true);

    let url = `/content/all?page=${page}&limit=12`;
    if (subject !== "All")    url += `&subject=${encodeURIComponent(subject)}`;
    if (typeFilter !== "All") url += `&type=${typeFilter}`;

    api.get(url)
      .then((r) => { setItems(r.data.content); setTotalPages(r.data.total_pages); })
      .catch(() => toast.error("Content load nahi hua."))
      .finally(() => setLoading(false));
  }, [contentId, subject, typeFilter, page]);

  // ── Load single content ──────────────────────────────────────
  useEffect(() => {
    if (!contentId) return;
    setDetailLoading(true);
    api.get(`/content/${contentId}`)
      .then((r) => {
        setContent(r.data.content);
        setIsCompleted(r.data.my_progress?.completed || false);
      })
      .catch(() => { toast.error("Content nahi mila."); navigate("/learn"); })
      .finally(() => setDetailLoading(false));
  }, [contentId]);

  // ── Search ───────────────────────────────────────────────────
  useEffect(() => {
    if (!search.trim() || contentId) return;
    const timer = setTimeout(async () => {
      try {
        const r = await api.get(`/content/search?q=${encodeURIComponent(search)}`);
        setItems(r.data.results);
        setTotalPages(1);
      } catch {}
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  const handleComplete = async (extra = {}) => {
    try {
      if (extra.rating) {
        await api.post(`/content/rate/${contentId}`, { rating: extra.rating });
        toast.success("Rating de di! ⭐");
      } else {
        await api.post(`/content/complete/${contentId}`, extra);
        setIsCompleted(true);
        setCompletedIds((prev) => [...prev, contentId]);
        toast.success("Content complete ho gaya! 🎉");
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Error aaya.");
    }
  };

  // ── DETAIL VIEW ──────────────────────────────────────────────
  if (contentId) {
    if (detailLoading) return <LoadingSpinner fullScreen message="Content load ho raha hai..." />;
    if (!content)      return null;

    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <button onClick={() => navigate("/learn")}
          className="flex items-center gap-2 text-gray-400 hover:text-white text-sm mb-6 transition">
          <ArrowLeft size={16}/> Wapas content list
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left — Player */}
          <div className="lg:col-span-2">
            <LecturePlayer
              content={content}
              onComplete={handleComplete}
              isCompleted={isCompleted}
            />
          </div>
          {/* Right — Summary + Chat */}
          <div>
            <SummaryPanel content={content} />
          </div>
        </div>
      </div>
    );
  }

  // ── LIST VIEW ────────────────────────────────────────────────
  const filtered = search.trim()
    ? items
    : items;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">📚 Content Library</h1>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        {/* Search */}
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"/>
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search content..."
            className="w-full bg-gray-800 border border-gray-700 text-white rounded-xl
                       pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500
                       transition placeholder-gray-500"/>
        </div>

        {/* Subject */}
        <select value={subject} onChange={(e) => { setSubject(e.target.value); setPage(1); }}
          className="bg-gray-800 border border-gray-700 text-white rounded-xl px-4 py-2.5
                     text-sm focus:outline-none focus:border-indigo-500 transition">
          {SUBJECTS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>

        {/* Type */}
        <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="bg-gray-800 border border-gray-700 text-white rounded-xl px-4 py-2.5
                     text-sm focus:outline-none focus:border-indigo-500 transition capitalize">
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {/* Recommended Banner */}
      {user?.learning_style && (
        <div className="mb-6 bg-indigo-900/20 border border-indigo-700/40 rounded-2xl px-5 py-3
                        flex items-center justify-between">
          <p className="text-indigo-300 text-sm">
            🎯 Tumhare liye recommendations dekhne ke liye Dashboard pe jao
          </p>
          <button onClick={() => navigate("/dashboard")}
            className="text-indigo-400 hover:text-white text-xs border border-indigo-700
                       px-3 py-1.5 rounded-lg transition">
            Dashboard
          </button>
        </div>
      )}

      {/* Grid */}
      {loading ? (
        <LoadingSpinner message="Content load ho raha hai..." />
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400">Koi content nahi mila. Filter change karo.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((item) => {
              const done = completedIds.includes(item.content_id);
              return (
                <div key={item.content_id}
                  onClick={() => navigate(`/learn/${item.content_id}`)}
                  className={`bg-gray-900 border rounded-2xl p-5 cursor-pointer transition group
                              ${done ? "border-emerald-700/50" : "border-gray-800 hover:border-indigo-600/50"}`}>
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-2xl">{TYPE_ICON[item.type] || "📚"}</span>
                    <div className="flex flex-col items-end gap-1">
                      <span className="bg-gray-800 text-gray-400 text-xs px-2 py-0.5 rounded-full capitalize">
                        {item.type}
                      </span>
                      {done && <span className="text-emerald-400 text-xs">✓ Done</span>}
                    </div>
                  </div>
                  <h3 className="text-white font-medium text-sm mb-2 group-hover:text-indigo-300
                                 transition line-clamp-2 leading-snug">
                    {item.title}
                  </h3>
                  <p className="text-gray-500 text-xs mb-3 line-clamp-2">{item.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>{item.subject}</span>
                    <span>{item.duration_min} min · {"★".repeat(item.difficulty)}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button onClick={() => setPage((p) => Math.max(1, p-1))} disabled={page===1}
                className="px-4 py-2 bg-gray-800 text-gray-400 rounded-xl disabled:opacity-30
                           hover:bg-gray-700 transition text-sm">
                ← Pehla
              </button>
              <span className="px-4 py-2 text-gray-400 text-sm">
                {page} / {totalPages}
              </span>
              <button onClick={() => setPage((p) => Math.min(totalPages, p+1))} disabled={page===totalPages}
                className="px-4 py-2 bg-gray-800 text-gray-400 rounded-xl disabled:opacity-30
                           hover:bg-gray-700 transition text-sm">
                Agla →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}