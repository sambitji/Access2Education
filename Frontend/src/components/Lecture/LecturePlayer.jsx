// frontend/src/components/Lecture/LecturePlayer.jsx
import { useState } from "react";
import ReactPlayer from "react-player";
import { FileText, Play, BookOpen, CheckCircle, Clock, Star } from "lucide-react";

const TYPE_ICON = { video:<Play size={16}/>, article:<FileText size={16}/>, exercise:<BookOpen size={16}/>, notes:<BookOpen size={16}/>, infographic:<FileText size={16}/>, tutorial:<BookOpen size={16}/>, project:<BookOpen size={16}/> };

export default function LecturePlayer({ content, onComplete, isCompleted }) {
  const [timeSpent, setTimeSpent]     = useState(0);
  const [rating, setRating]           = useState(0);
  const [hoverStar, setHoverStar]     = useState(0);
  const [showRating, setShowRating]   = useState(false);

  const handleComplete = () => {
    onComplete({ time_spent_min: Math.round(timeSpent / 60) });
    setShowRating(true);
  };

  const handleRating = async (stars) => {
    setRating(stars);
    await onComplete({ rating: stars });
    setShowRating(false);
  };

  const isVideo = content.type === "video";

  return (
    <div className="space-y-5">

      {/* Content Header */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-indigo-900/50 rounded-xl flex items-center
                          justify-center text-indigo-400 shrink-0">
            {TYPE_ICON[content.type] || <BookOpen size={16}/>}
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-white font-bold text-lg leading-tight mb-1">{content.title}</h1>
            <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
              <span className="capitalize bg-gray-800 px-2 py-1 rounded-lg">{content.type}</span>
              <span>{content.subject}</span>
              <span className="flex items-center gap-1"><Clock size={11}/>{content.duration_min} min</span>
              <span>{"⭐".repeat(content.difficulty)}</span>
            </div>
          </div>
          {isCompleted && (
            <div className="flex items-center gap-1 text-emerald-400 text-sm shrink-0">
              <CheckCircle size={16}/> Done
            </div>
          )}
        </div>
      </div>

      {/* Video Player */}
      {isVideo && content.url && (
        <div className="bg-black rounded-2xl overflow-hidden aspect-video">
          <ReactPlayer
            url={content.url}
            width="100%" height="100%"
            controls
            onProgress={({ playedSeconds }) => setTimeSpent(playedSeconds)}
            config={{ youtube:{ playerVars:{ modestbranding:1 } } }}
          />
        </div>
      )}

      {/* Article / Notes Content */}
      {(content.type === "article" || content.type === "notes") && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <p className="text-gray-300 leading-relaxed text-sm">{content.description}</p>
          {content.url && (
            <a href={content.url} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-2 mt-4 text-indigo-400 hover:text-indigo-300
                          text-sm border border-indigo-700 px-4 py-2 rounded-xl transition">
              <FileText size={14}/> Full Content Padho
            </a>
          )}
        </div>
      )}

      {/* Exercise / Project */}
      {(content.type === "exercise" || content.type === "project") && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <h3 className="text-white font-semibold mb-2">📝 Description</h3>
          <p className="text-gray-300 text-sm leading-relaxed mb-4">{content.description}</p>
          {content.url && (
            <a href={content.url} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-2 text-indigo-400 hover:text-indigo-300
                          text-sm border border-indigo-700 px-4 py-2 rounded-xl transition">
              <Play size={14}/> Start {content.type === "project" ? "Project" : "Exercise"}
            </a>
          )}
        </div>
      )}

      {/* Complete Button */}
      {!isCompleted && (
        <button onClick={handleComplete}
          className="w-full flex items-center justify-center gap-2 bg-emerald-600
                     hover:bg-emerald-700 text-white font-semibold py-3.5 rounded-xl transition">
          <CheckCircle size={18}/> Complete Mark Karo ✓
        </button>
      )}

      {/* Rating */}
      {showRating && (
        <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 text-center">
          <p className="text-white font-semibold mb-1">Ye content kaisa laga?</p>
          <p className="text-gray-400 text-sm mb-4">Rating do taaki hum better recommend kar sakein</p>
          <div className="flex justify-center gap-2">
            {[1,2,3,4,5].map((s) => (
              <button key={s}
                onClick={() => handleRating(s)}
                onMouseEnter={() => setHoverStar(s)}
                onMouseLeave={() => setHoverStar(0)}
                className="text-3xl transition-transform hover:scale-125">
                <Star fill={(hoverStar||rating) >= s ? "#f59e0b" : "none"}
                      stroke={(hoverStar||rating) >= s ? "#f59e0b" : "#6b7280"}
                      size={32} />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}