// frontend/src/components/AptitudeTest/QuestionCard.jsx
import { CheckCircle, Circle } from "lucide-react";

const SECTION_COLORS = {
  logical:   "indigo",
  verbal:    "violet",
  numerical: "emerald",
  memory:    "amber",
  attention: "rose",
};

export default function QuestionCard({ question, selectedAnswer, onAnswer, questionNumber, totalQuestions }) {
  const color = SECTION_COLORS[question.section] || "indigo";

  const colorMap = {
    indigo:  { badge:"bg-indigo-900/50 text-indigo-300 border-indigo-700",  selected:"border-indigo-500 bg-indigo-900/30 text-white", dot:"bg-indigo-500" },
    violet:  { badge:"bg-violet-900/50 text-violet-300 border-violet-700",  selected:"border-violet-500 bg-violet-900/30 text-white",  dot:"bg-violet-500" },
    emerald: { badge:"bg-emerald-900/50 text-emerald-300 border-emerald-700",selected:"border-emerald-500 bg-emerald-900/30 text-white",dot:"bg-emerald-500"},
    amber:   { badge:"bg-amber-900/50 text-amber-300 border-amber-700",     selected:"border-amber-500 bg-amber-900/30 text-white",    dot:"bg-amber-500" },
    rose:    { badge:"bg-rose-900/50 text-rose-300 border-rose-700",        selected:"border-rose-500 bg-rose-900/30 text-white",      dot:"bg-rose-500" },
  };
  const c = colorMap[color];

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <span className={`text-xs px-3 py-1 rounded-full border capitalize ${c.badge}`}>
          {question.section}
        </span>
        <span className="text-gray-500 text-sm">
          Q{questionNumber} / {totalQuestions}
        </span>
      </div>

      {/* Question */}
      <p className="text-white text-base leading-relaxed mb-6 whitespace-pre-line">
        {question.question}
      </p>

      {/* Options */}
      <div className="space-y-3">
        {question.options.map((option, i) => {
          const isSelected = selectedAnswer === option;
          const letters    = ["A", "B", "C", "D"];
          return (
            <button key={i} onClick={() => onAnswer(question.id, option)}
              className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl border text-sm
                          text-left transition-all duration-200
                          ${isSelected
                            ? `${c.selected} border`
                            : "border-gray-700 bg-gray-800/50 text-gray-300 hover:border-gray-500 hover:bg-gray-800"}`}>
              <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0
                               ${isSelected ? c.dot + " text-white" : "bg-gray-700 text-gray-400"}`}>
                {letters[i]}
              </span>
              <span className="flex-1">{option}</span>
              {isSelected && <CheckCircle size={18} className="shrink-0 text-current" />}
            </button>
          );
        })}
      </div>

      {/* Marks */}
      <div className="mt-4 text-right text-xs text-gray-500">
        {question.marks} marks
      </div>
    </div>
  );
}