"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Message, ChatResponse } from "./types";

const SUGGESTED_QUESTIONS = [
  "What programmes does SIST Tangier offer?",
  "How do I apply for admission?",
  "Are there scholarships available?",
  "What is the foundation year?",
];

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const startNewChat = () => {
    if (messages.length > 0) {
      const newSession: ChatSession = {
        id: activeSessionId || crypto.randomUUID(),
        title: messages[0]?.content.slice(0, 42) + (messages[0]?.content.length > 42 ? "..." : "") || "New conversation",
        messages,
        createdAt: new Date(),
      };
      setSessions((prev) => {
        const exists = prev.find((s) => s.id === newSession.id);
        if (exists) return prev.map((s) => s.id === newSession.id ? newSession : s);
        return [newSession, ...prev];
      });
    }
    setMessages([]);
    setSessionId(null);
    setActiveSessionId(null);
  };

  const loadSession = (session: ChatSession) => {
    if (messages.length > 0 && activeSessionId !== session.id) {
      const current: ChatSession = {
        id: activeSessionId || crypto.randomUUID(),
        title: messages[0]?.content.slice(0, 42) + "..." || "New conversation",
        messages,
        createdAt: new Date(),
      };
      setSessions((prev) => {
        const exists = prev.find((s) => s.id === current.id);
        if (exists) return prev.map((s) => s.id === current.id ? current : s);
        return [current, ...prev];
      });
    }
    setMessages(session.messages);
    setSessionId(session.id);
    setActiveSessionId(session.id);
  };

  const deleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (activeSessionId === id) {
      setMessages([]);
      setSessionId(null);
      setActiveSessionId(null);
    }
  };

  const sendMessage = async (question: string) => {
    if (!question.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post<ChatResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/chat`,
        { question, session_id: sessionId },
        { timeout: 120000 }
      );
      if (!sessionId) setSessionId(res.data.session_id);
      setTimeout(() => {
        setMessages((prev) => [...prev, { role: "assistant", content: res.data.answer }]);
      }, 600);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "The assistant could not be reached. Please ensure the backend is running and try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex h-screen bg-[#070d1a] text-white overflow-hidden" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        .msg-in { animation: msgIn 0.25s ease forwards; }
        @keyframes msgIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .dot { animation: dotPulse 1.4s infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes dotPulse { 0%,80%,100%{opacity:0.2} 40%{opacity:1} }
        .session-row:hover .del-btn { opacity: 1; }
        .del-btn { opacity: 0; transition: opacity 0.15s; }
      `}</style>

      {/* Sidebar */}
      <aside
        style={{ width: sidebarOpen ? "256px" : "0px", minWidth: sidebarOpen ? "256px" : "0px", overflow: "hidden", transition: "all 0.25s ease" }}
        className="flex flex-col bg-[#0b1424] border-r border-white/[0.06]"
      >
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/[0.06]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">History</span>
          <button
            onClick={startNewChat}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition-colors"
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            New chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-2 px-2">
          {sessions.length === 0 ? (
            <p className="px-3 py-6 text-xs text-slate-600 text-center leading-5">No previous conversations.<br />Start chatting to build history.</p>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => loadSession(s)}
                className={`session-row relative flex items-start gap-2 rounded-lg px-3 py-2.5 mb-0.5 cursor-pointer transition-colors ${
                  activeSessionId === s.id ? "bg-blue-600/20 border border-blue-500/25" : "hover:bg-white/[0.04] border border-transparent"
                }`}
              >
                <svg className="mt-0.5 shrink-0 text-slate-500" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-slate-300 truncate leading-5">{s.title}</p>
                  <p className="text-[10px] text-slate-600 mt-0.5">
                    {s.createdAt.toLocaleDateString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                  </p>
                </div>
                <button onClick={(e) => deleteSession(s.id, e)} className="del-btn shrink-0 mt-0.5 text-slate-600 hover:text-red-400 transition-colors">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-white/[0.06] bg-[#0b1424]/90 backdrop-blur-sm px-5 py-3 shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="rounded-md p-1.5 text-slate-500 hover:text-white hover:bg-white/[0.06] transition-colors">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            </button>
            <div className="flex items-center gap-2.5">
              <div className="flex items-center justify-center rounded-md border border-white/20 bg-white/90 px-2 py-1">
                <img src="/sist-logo.png" alt="SIST" className="h-7 w-auto object-contain" />
              </div>
              <div className="flex items-center justify-center rounded-md border border-white/20 bg-white/90 px-2 py-1">
                <img src="/cardiffmet-logo.png" alt="Cardiff Met" className="h-7 w-auto object-contain" />
              </div>
            </div>
            <div className="pl-1 border-l border-white/10">
              <h1 className="text-sm font-semibold text-white leading-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>SIST Tangier</h1>
              <p className="text-[11px] text-slate-500 leading-tight">University AI Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] font-medium text-emerald-400">Online</span>
          </div>
        </header>

        {/* Chat area */}
        <section className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex min-h-full max-w-2xl flex-col">
            {messages.length === 0 ? (
              <div className="flex flex-1 items-center justify-center">
                <div className="w-full">
                  <div className="mb-8 text-center">
                    <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600/15 border border-blue-500/25">
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    </div>
                    <h2 className="mb-2 text-xl font-semibold text-white" style={{ fontFamily: "'DM Serif Display', serif" }}>
                      SIST Tangier AI Assistant
                    </h2>
                    <p className="text-sm text-slate-500 leading-6 max-w-sm mx-auto">
                      Ask about programmes, admissions, scholarships, foundation year, and student life at SIST Tangier.
                    </p>
                  </div>

                  <div className="mb-4 grid grid-cols-3 gap-3">
                    {[
                      {
                        icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>,
                        title: "Programmes", desc: "Courses and study options"
                      },
                      {
                        icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>,
                        title: "Admissions", desc: "Apply and required documents"
                      },
                      {
                        icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
                        title: "Student Help", desc: "General university guidance"
                      },
                    ].map((c) => (
                      <div key={c.title} className="rounded-xl border border-white/[0.07] bg-white/[0.03] p-4">
                        <div className="mb-2 text-slate-400">{c.icon}</div>
                        <h3 className="mb-1 text-xs font-semibold text-white">{c.title}</h3>
                        <p className="text-[11px] text-slate-600 leading-4">{c.desc}</p>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {SUGGESTED_QUESTIONS.map((q) => (
                      <button
                        key={q}
                        onClick={() => sendMessage(q)}
                        className="rounded-xl border border-white/[0.07] bg-white/[0.02] px-4 py-3 text-left text-xs text-slate-400 transition-all hover:border-blue-500/30 hover:bg-blue-500/10 hover:text-white"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4 pb-2">
                {messages.map((msg, i) => (
                  <div key={i} className={`msg-in flex gap-2.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    {msg.role === "assistant" && (
                      <div className="shrink-0 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-blue-600/20 border border-blue-500/25">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                      </div>
                    )}
                    <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-6 ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-tr-sm"
                        : "border border-white/[0.07] bg-white/[0.04] text-slate-200 rounded-tl-sm"
                    }`}>
                      {msg.content}
                    </div>
                    {msg.role === "user" && (
                      <div className="shrink-0 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-slate-700/80 border border-white/10">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="msg-in flex gap-2.5 justify-start">
                    <div className="shrink-0 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-blue-600/20 border border-blue-500/25">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    </div>
                    <div className="rounded-2xl rounded-tl-sm border border-white/[0.07] bg-white/[0.04] px-4 py-3 flex gap-1.5 items-center">
                      <span className="dot h-1.5 w-1.5 rounded-full bg-slate-400"></span>
                      <span className="dot h-1.5 w-1.5 rounded-full bg-slate-400"></span>
                      <span className="dot h-1.5 w-1.5 rounded-full bg-slate-400"></span>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            )}
          </div>
        </section>

        {/* Input */}
        <footer className="border-t border-white/[0.06] bg-[#0b1424]/90 backdrop-blur-sm px-4 py-3 shrink-0">
          <div className="mx-auto flex max-w-2xl gap-2 rounded-xl border border-white/[0.08] bg-white/[0.04] p-1.5">
            <input
              className="flex-1 bg-transparent px-3 text-sm text-white outline-none placeholder:text-slate-600"
              placeholder="Ask about SIST Tangier..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage(input)}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={loading || !input.trim()}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-blue-500 disabled:opacity-30"
            >
              Send
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
          <p className="mt-1.5 text-center text-[10px] text-slate-700">SIST Tangier · Powered by Retrieval-Augmented Generation</p>
        </footer>
      </div>
    </main>
  );
}