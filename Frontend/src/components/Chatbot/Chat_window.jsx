// frontend/src/components/Chatbot/ChatWindow.jsx
import { useState, useRef, useEffect } from "react";
import { Send, Bot, X, Minimize2, Maximize2, Sparkles } from "lucide-react";
import api from "../../services/api";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ lectureContext = "", onClose }) {
  const [messages, setMessages] = useState([
    { role:"assistant", content:"Namaste! 👋 Main tumhara AI assistant hoon. Is lecture ke baare mein kuch bhi poocho ya summary lene ke liye 'summarize' likho!", timestamp: new Date() }
  ]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [minimized, setMinimized] = useState(false);
  const bottomRef               = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:"smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    const userMsg = text || input.trim();
    if (!userMsg || loading) return;
    setInput("");

    const userBubble = { role:"user", content:userMsg, timestamp:new Date() };
    setMessages((prev) => [...prev, userBubble]);
    setLoading(true);

    try {
      const isSummary = /summarize|summary|samjhao|kya hai|explain/i.test(userMsg);
      const endpoint  = isSummary ? "/chatbot/summarize" : "/chatbot/ask";
      const payload   = isSummary
        ? { lecture_text: lectureContext || userMsg }
        : { question: userMsg, lecture_context: lectureContext };

      const res = await api.post(endpoint, payload);
      const reply = res.data.summary || res.data.answer || "Maafi, samajh nahi aaya.";

      setMessages((prev) => [...prev, { role:"assistant", content:reply, timestamp:new Date() }]);
    } catch {
      setMessages((prev) => [...prev, {
        role:"assistant",
        content:"Oops! Kuch gadbad ho gayi. Dobara try karo.",
        timestamp: new Date(),
        isError: true,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = ["Summarize karo", "Simple karo", "Examples do"];

  return (
    <div className={`flex flex-col bg-gray-900 border border-gray-700 rounded-2xl overflow-hidden
                     shadow-2xl transition-all duration-300
                     ${minimized ? "h-14" : "h-[480px]"} w-full`}>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
            <Bot size={16} className="text-white" />
          </div>
          <div>
            <p className="text-white text-sm font-semibold">AI Assistant</p>
            <p className="text-gray-400 text-xs">DeepSeek powered</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setMinimized(!minimized)}
            className="text-gray-500 hover:text-white p-1.5 rounded-lg hover:bg-gray-700 transition">
            {minimized ? <Maximize2 size={14}/> : <Minimize2 size={14}/>}
          </button>
          {onClose && (
            <button onClick={onClose}
              className="text-gray-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-gray-700 transition">
              <X size={14}/>
            </button>
          )}
        </div>
      </div>

      {!minimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-700">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Bot size={16} className="text-indigo-400" />
                <div className="flex gap-1">
                  {[0,1,2].map((i) => (
                    <span key={i} className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                          style={{ animationDelay:`${i*0.15}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick Actions */}
          <div className="px-4 pb-2 flex gap-2 overflow-x-auto">
            {quickActions.map((action) => (
              <button key={action} onClick={() => sendMessage(action)}
                className="text-xs bg-gray-800 hover:bg-gray-700 border border-gray-700
                           text-gray-300 px-3 py-1.5 rounded-full whitespace-nowrap transition flex items-center gap-1">
                <Sparkles size={10}/> {action}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="px-4 pb-4 pt-2 border-t border-gray-800">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                placeholder="Kuch bhi poocho..."
                className="flex-1 bg-gray-800 border border-gray-700 text-white rounded-xl
                           px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500
                           transition placeholder-gray-500"
              />
              <button onClick={() => sendMessage()} disabled={loading || !input.trim()}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white
                           p-2.5 rounded-xl transition">
                <Send size={16}/>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}