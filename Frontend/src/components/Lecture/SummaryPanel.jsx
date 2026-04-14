// frontend/src/components/Lecture/SummaryPanel.jsx
import { useState } from "react";
import { Sparkles, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import ChatWindow from "../Chatbot/ChatWindow";

export default function SummaryPanel({ content }) {
  const [showChat, setShowChat]     = useState(false);
  const [expanded, setExpanded]     = useState(true);

  const lectureContext = `
    Title: ${content?.title || ""}
    Subject: ${content?.subject || ""}
    Type: ${content?.type || ""}
    Description: ${content?.description || ""}
  `.trim();

  return (
    <div className="space-y-4">

      {/* Description Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <button onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800/50 transition">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Sparkles size={16} className="text-indigo-400"/> About This Content
          </div>
          {expanded ? <ChevronUp size={16} className="text-gray-500"/> : <ChevronDown size={16} className="text-gray-500"/>}
        </button>

        {expanded && (
          <div className="px-5 pb-5">
            <p className="text-gray-300 text-sm leading-relaxed">{content?.description}</p>

            <div className="mt-4 flex flex-wrap gap-2">
              {content?.tags?.map((tag, i) => (
                <span key={i} className="bg-gray-800 border border-gray-700 text-gray-400
                                          text-xs px-2.5 py-1 rounded-full">
                  #{tag}
                </span>
              ))}
            </div>

            {content?.prerequisites?.length > 0 && (
              <div className="mt-4">
                <p className="text-gray-400 text-xs mb-2">Prerequisites:</p>
                <div className="flex flex-wrap gap-2">
                  {content.prerequisites.map((p) => (
                    <span key={p} className="bg-amber-900/20 border border-amber-700/40
                                              text-amber-400 text-xs px-2 py-0.5 rounded-full">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Chatbot Toggle */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <button onClick={() => setShowChat(!showChat)}
          className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800/50 transition">
          <div className="flex items-center gap-2 text-white font-semibold">
            <MessageSquare size={16} className="text-indigo-400"/> AI Assistant
          </div>
          <div className="flex items-center gap-2">
            {showChat ? <ChevronUp size={16} className="text-gray-500"/> : <ChevronDown size={16} className="text-gray-500"/>}
          </div>
        </button>

        {showChat && (
          <div className="px-4 pb-4">
            <ChatWindow lectureContext={lectureContext} />
          </div>
        )}
      </div>
    </div>
  );
}