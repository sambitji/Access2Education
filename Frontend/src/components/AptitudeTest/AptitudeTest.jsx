// frontend/src/components/AptitudeTest/AptitudeTest.jsx
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Clock, ChevronLeft, ChevronRight, Send, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import api from "../../services/api";
import QuestionCard from "./QuestionCard";
import useAuthStore from "../../store/authStore";

const TOTAL_MINUTES = 30;

export default function AptitudeTest({ sections }) {
  const navigate              = useNavigate();
  const { setLearningStyle }  = useAuthStore();
  const [currentSection, setCurrentSection] = useState(0);
  const [currentQ, setCurrentQ]             = useState(0);
  const [answers, setAnswers]               = useState({});
  const [timeLeft, setTimeLeft]             = useState(TOTAL_MINUTES * 60);
  const [submitting, setSubmitting]         = useState(false);

  // Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) { clearInterval(timer); handleSubmit(); return 0; }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (s) => `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;

  const allQuestions = sections.flatMap((s) => s.questions);
  const totalQs      = allQuestions.length;
  const answered     = Object.keys(answers).length;
  const progress     = Math.round((answered / totalQs) * 100);

  const section    = sections[currentSection];
  const question   = section?.questions[currentQ];

  const handleAnswer = (qId, answer) => setAnswers((prev) => ({ ...prev, [qId]: answer }));

  const handleNext = () => {
    if (currentQ < section.questions.length - 1) {
      setCurrentQ(currentQ + 1);
    } else if (currentSection < sections.length - 1) {
      setCurrentSection(currentSection + 1);
      setCurrentQ(0);
    }
  };

  const handlePrev = () => {
    if (currentQ > 0) {
      setCurrentQ(currentQ - 1);
    } else if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
      setCurrentQ(sections[currentSection - 1].questions.length - 1);
    }
  };

  const handleSubmit = useCallback(async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      const answersArr = allQuestions.map((q) => ({
        question_id: q.id,
        answer:      answers[q.id] || "",
      }));
      const res = await api.post("/test/submit", { answers: answersArr });
      setLearningStyle(res.data.learning_style, res.data.cluster_id);
      toast.success("Test submit ho gaya! 🎉");
      navigate("/test/result");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Submit failed.");
      setSubmitting(false);
    }
  }, [answers, submitting]);

  const isFirst = currentSection === 0 && currentQ === 0;
  const isLast  = currentSection === sections.length - 1 &&
                  currentQ === section.questions.length - 1;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">

      {/* Timer + Progress */}
      <div className="flex items-center justify-between mb-6">
        <div className={`flex items-center gap-2 font-mono text-lg font-bold px-4 py-2 rounded-xl
                        ${timeLeft < 300 ? "bg-red-900/50 text-red-400 border border-red-700"
                                         : "bg-gray-800 text-white"}`}>
          <Clock size={18} /> {formatTime(timeLeft)}
        </div>
        <span className="text-gray-400 text-sm">{answered}/{totalQs} answered</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-800 rounded-full h-2 mb-6">
        <div className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
             style={{ width: `${progress}%` }} />
      </div>

      {/* Section tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
        {sections.map((s, i) => {
          const sAnswered = s.questions.filter((q) => answers[q.id]).length;
          return (
            <button key={i} onClick={() => { setCurrentSection(i); setCurrentQ(0); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition
                          ${i === currentSection
                            ? "bg-indigo-600 text-white"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>
              {s.section_name} ({sAnswered}/{s.questions.length})
            </button>
          );
        })}
      </div>

      {/* Question */}
      {question && (
        <QuestionCard
          question={question}
          selectedAnswer={answers[question.id]}
          onAnswer={handleAnswer}
          questionNumber={
            sections.slice(0, currentSection).reduce((a, s) => a + s.questions.length, 0) + currentQ + 1
          }
          totalQuestions={totalQs}
        />
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6">
        <button onClick={handlePrev} disabled={isFirst}
          className="flex items-center gap-2 px-4 py-2.5 bg-gray-800 hover:bg-gray-700
                     disabled:opacity-30 text-white rounded-xl transition text-sm">
          <ChevronLeft size={18} /> Pehla
        </button>

        {isLast ? (
          <button onClick={handleSubmit} disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700
                       disabled:opacity-50 text-white font-semibold rounded-xl transition">
            {submitting
              ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"/>
              : <><Send size={18}/> Submit Test</>}
          </button>
        ) : (
          <button onClick={handleNext}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700
                       text-white rounded-xl transition text-sm">
            Agla <ChevronRight size={18} />
          </button>
        )}
      </div>

      {/* Unanswered warning */}
      {isLast && answered < totalQs && (
        <div className="mt-4 flex items-center gap-2 bg-amber-900/30 border border-amber-700
                        text-amber-400 px-4 py-3 rounded-xl text-sm">
          <AlertCircle size={16} />
          {totalQs - answered} questions unanswered hain. Submit karne pe woh blank rahenge.
        </div>
      )}
    </div>
  );
}