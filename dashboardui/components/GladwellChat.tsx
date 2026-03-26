"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  MessageSquare, 
  Send, 
  X, 
  Bot, 
  User, 
  Sparkles, 
  ArrowUpRight, 
  Trash2, 
  ChevronDown, 
  ChevronUp,
  Store,
  Box
} from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface GladwellChatProps {
  summary: {
    total_branches: number;
    total_products: number;
    total_revenue: number;
    avg_margin: number;
  } | null;
}

export default function GladwellChat({ summary }: GladwellChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isQuickOpen, setIsQuickOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (customMsg?: string) => {
    const text = customMsg || input;
    if (!text.trim() || isLoading) return;

    const userMsg = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    if (!customMsg) setInput("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/api/chat/analyst", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ messages: [...messages, userMsg] })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "I'm having trouble connecting to the intelligence core. Please check your session." }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", content: "Analytic sync failed. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const quickQuestions = [
    { text: "Top Branch?", q: "Which branch has the highest revenue right now?" },
    { text: "Stock Risks?", q: "Are there any products at high risk of stockout?" },
    { text: "Low Margins?", q: "Show me products with margins below 5%." },
    { text: "Revenue Summary", q: "Give me a quick summary of overall business performance." }
  ];

  return (
    <div className="fixed bottom-10 right-10 z-[100]">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9, filter: "blur(10px)" }}
            animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: 50, scale: 0.9, filter: "blur(10px)" }}
            className="fixed bottom-32 right-10 w-[420px] h-[min(650px,80vh)] bg-[#0A0B10] rounded-[32px] shadow-2xl z-[99] flex flex-col overflow-hidden border border-white/5"
          >
            {/* Header: Emerald Green as per screenshot */}
            <div className="bg-emerald-600 px-6 py-4 flex items-center justify-between text-white shadow-lg shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center p-1.5 shadow-inner">
                   <div className="w-full h-full bg-emerald-100 rounded-full flex items-center justify-center font-black text-emerald-800 text-xs">GAI</div>
                </div>
                <h3 className="font-bold text-lg tracking-tight">Gladwell</h3>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={clearChat} className="p-2 hover:bg-white/10 rounded-xl transition-colors shrink-0">
                  <Trash2 className="w-5 h-5 text-white/70 hover:text-white" />
                </button>
                <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-xl transition-colors shrink-0">
                  <X className="w-5 h-5 text-white/70 hover:text-white" />
                </button>
              </div>
            </div>

            {/* Chat Area */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
              {messages.length === 0 ? (
                /* Welcome Screen */
                <div className="flex flex-col items-center justify-center pt-8 text-center px-4 animate-in fade-in duration-1000">
                  <div className="relative mb-8">
                     <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-xl p-2">
                        <div className="w-full h-full bg-emerald-50 rounded-full flex items-center justify-center text-emerald-600">
                           <Bot className="w-12 h-12" />
                        </div>
                     </div>
                     <div className="absolute -top-1 -right-1 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center shadow-lg border-2 border-[#0A0B10]">
                        <Sparkles className="w-4 h-4 text-white" />
                     </div>
                  </div>
                  
                  <h2 className="text-3xl font-black text-white mb-4">Hi! I'm Gladwell</h2>
                  <p className="text-zinc-400 text-sm leading-relaxed mb-8 max-w-[280px]">
                    Your friendly Msingi Intelligence assistant. I'm here to help you with branch data, sales trends, and more 📊
                  </p>

                  <div className="grid grid-cols-2 gap-4 w-full max-w-sm">
                    <div className="bg-indigo-600/10 border border-indigo-500/20 p-6 rounded-[24px] flex flex-col items-center">
                       <Store className="w-8 h-8 text-indigo-400 mb-3" />
                       <span className="text-2xl font-black text-white">{summary?.total_branches ?? 0}</span>
                       <span className="text-[10px] uppercase tracking-widest font-bold text-indigo-300/60 mt-1">Branches</span>
                    </div>
                    <div className="bg-pink-600/10 border border-pink-500/20 p-6 rounded-[24px] flex flex-col items-center">
                       <Box className="w-8 h-8 text-pink-400 mb-3" />
                       <span className="text-2xl font-black text-white">{summary?.total_products?.toLocaleString() ?? 0}</span>
                       <span className="text-[10px] uppercase tracking-widest font-bold text-pink-300/60 mt-1">Products</span>
                    </div>
                  </div>

                  <p className="text-emerald-500 text-[11px] font-bold uppercase tracking-[0.2em] mt-12 animate-bounce">
                    Type a message below to get started ↓
                  </p>
                </div>
              ) : (
                /* Message List */
                messages.map((m, i) => (
                  <div key={i} className={cn("flex w-full", m.role === "user" ? "justify-end" : "justify-start")}>
                    <div className={cn(
                      "max-w-[90%] px-4 py-2.5 rounded-2xl text-[13px] leading-relaxed font-semibold shadow-md transition-all",
                      m.role === "user" 
                        ? "bg-purple-600 text-white rounded-br-none" 
                        : "bg-zinc-900 text-zinc-300 rounded-bl-none border border-white/5"
                    )}>
                      {m.content}
                    </div>
                  </div>
                ))
              )}

              {isLoading && (
                 <div className="flex justify-start">
                    <div className="bg-zinc-900 border border-white/5 rounded-2xl p-4 flex gap-1.5 shadow-inner">
                       <span className="w-1.5 h-1.5 bg-emerald-500/50 rounded-full animate-bounce delay-75"></span>
                       <span className="w-1.5 h-1.5 bg-emerald-500/70 rounded-full animate-bounce delay-150"></span>
                       <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce delay-300"></span>
                    </div>
                 </div>
              )}
            </div>

            {/* Input & Quick Questions Bar */}
            <div className="px-6 pb-6 pt-2 bg-[#0A0B10] space-y-4">
              {/* Expandable Quick Questions */}
              <div className="rounded-2xl border border-white/5 bg-zinc-900/50 overflow-hidden transition-all duration-300">
                <button 
                  onClick={() => setIsQuickOpen(!isQuickOpen)}
                  className="w-full px-4 py-3 flex items-center justify-between text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-emerald-500 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3 h-3" />
                    <span>Quick Questions</span>
                  </div>
                  {isQuickOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                </button>
                <motion.div 
                  initial={false}
                  animate={{ height: isQuickOpen ? "auto" : 0 }}
                  className="overflow-hidden"
                >
                   <div className="px-4 pb-4 flex flex-wrap gap-2">
                      {quickQuestions.map((qq, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(qq.q)}
                          className="px-3 py-2 bg-zinc-800 hover:bg-emerald-600/20 hover:text-emerald-400 border border-white/5 rounded-xl text-xs font-semibold text-zinc-400 transition-all"
                        >
                          {qq.text}
                        </button>
                      ))}
                   </div>
                </motion.div>
              </div>

              {/* Input Bar */}
              <div className="relative flex items-center gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Ask anything... (Enter to send)"
                  className="flex-1 bg-zinc-900 border border-white/5 rounded-2xl px-6 py-4 text-sm font-semibold text-white focus:ring-2 focus:ring-emerald-600/20 transition-all outline-none"
                />
                <button 
                  onClick={() => handleSend()}
                  disabled={isLoading}
                  className="p-4 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-600/20 group disabled:opacity-50"
                >
                  <Send className={cn("w-5 h-5 transition-transform group-hover:scale-110", isLoading && "animate-pulse")} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* FAB: Purple/Blue Gradient circular trigger */}
      <motion.button
        whileHover={{ scale: 1.05, filter: "brightness(1.1)" }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="relative w-16 h-16 bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 text-white rounded-full shadow-2xl flex items-center justify-center group"
      >
        <div className="absolute inset-0 bg-white/20 rounded-full blur-xl opacity-0 group-hover:opacity-40 transition-opacity"></div>
        {isOpen ? <X className="w-8 h-8" /> : <Send className="w-8 h-8 rotate-[-45deg] translate-x-1 -translate-y-1" />}
        
        {/* AI Badge Pill as per screenshot */}
        {!isOpen && (
          <div className="absolute -top-1 -right-1 bg-gradient-to-r from-pink-500 to-orange-500 px-2 py-0.5 rounded-full border-2 border-[#0A0B10] shadow-lg">
             <span className="text-[10px] font-black tracking-tighter text-white">AI</span>
          </div>
        )}

        {/* Floating Sparkles for Vibe */}
        {!isOpen && (
          <>
            <Sparkles className="absolute -top-4 -left-2 w-5 h-5 text-purple-400 animate-pulse" />
            <Sparkles className="absolute -bottom-2 -left-6 w-3 h-3 text-emerald-400 animate-pulse delay-700" />
          </>
        )}
      </motion.button>
    </div>
  );
}
