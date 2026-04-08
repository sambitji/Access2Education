// frontend/src/components/Chatbot/MessageBubble.jsx
import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const time   = new Date(message.timestamp).toLocaleTimeString("en-IN",
                   { hour:"2-digit", minute:"2-digit" });

  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5
                      ${isUser ? "bg-indigo-600" : "bg-gray-700"}`}>
        {isUser ? <User size={14} className="text-white" /> : <Bot size={14} className="text-indigo-400" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed
                        ${isUser
                          ? "bg-indigo-600 text-white rounded-tr-sm"
                          : message.isError
                            ? "bg-red-900/30 border border-red-700 text-red-300 rounded-tl-sm"
                            : "bg-gray-800 text-gray-200 rounded-tl-sm"}`}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p:      ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({children}) => <strong className="text-white font-semibold">{children}</strong>,
                code:   ({children}) => <code className="bg-gray-900 text-indigo-300 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>,
                ul:     ({children}) => <ul className="list-disc pl-4 space-y-1 my-2">{children}</ul>,
                ol:     ({children}) => <ol className="list-decimal pl-4 space-y-1 my-2">{children}</ol>,
                li:     ({children}) => <li className="text-sm">{children}</li>,
                h3:     ({children}) => <h3 className="text-white font-semibold mt-3 mb-1">{children}</h3>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        <span className="text-gray-600 text-xs px-1">{time}</span>
      </div>
    </div>
  );
}