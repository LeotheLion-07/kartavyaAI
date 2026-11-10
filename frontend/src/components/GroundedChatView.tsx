"use client";

import React, { useState } from "react";
import {
  MessageSquare,
  Send,
  ShieldCheck,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export function GroundedChatView() {
  const { currentProject } = useAuth();
  const [messages, setMessages] = useState<any[]>([
    {
      role: "assistant",
      content:
        "Hello Marcus! I am your grounded handover copilot. I answer strictly from verified Git PRs, RFC memos, and approved architecture discussions. Every fact includes verifiable source citations.",
      citations: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "What is the database pool setup?",
    "What tasks are unfinished?",
    "Why was this technology selected?",
    "Who owns the webhook retry queue?",
    "What are the major blockers?",
    "What should I work on first?",
    "What is the secret recipe for cafeteria brownies?",
  ];

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || input;
    if (!q.trim() || loading) return;

    const userMsg = { role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.queryChat({
        project_id: currentProject.id,
        query: q,
      });

      const assistantMsg = {
        role: "assistant",
        content: res.answer,
        isGrounded: res.is_grounded,
        citations: res.citations || [],
        redactedCount: res.redacted_items_count,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${e.message}`,
          isGrounded: false,
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto flex flex-col h-[calc(100vh-4rem)] overflow-hidden">
      {/* Header */}
      <div className="border-b border-[#E5D5BF] pb-4 mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-[#4E5D52] text-white shadow-xs">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base sm:text-lg font-bold text-[#222B25]">
                Grounded Handover Assistant
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                Zero Hallucination
              </span>
            </div>
            <p className="text-xs text-[#5E6F63]">
              Only answers using approved, permitted project evidence with exact citations.
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-2 text-xs font-mono text-[#5E6F63]">
          <ShieldCheck className="w-4 h-4 text-[#4E5D52]" />
          <span>BFT Consensus Grounded</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
                msg.role === "user"
                  ? "bg-[#4E5D52] text-white shadow-xs"
                  : "bg-white border border-[#E5D5BF] text-[#222B25] shadow-2xs"
              }`}
            >
              <div className="whitespace-pre-line font-sans">{msg.content}</div>

              {/* Citations Box */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="pt-3 border-t border-[#E5D5BF] space-y-2">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-[#8B968D] flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#4E5D52]" />
                    <span>Verifiable Evidence Citations:</span>
                  </div>
                  <div className="space-y-1.5">
                    {msg.citations.map((c: any, i: number) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-lg bg-[#EFF3ED] border border-[#A6B29C] text-[11px] space-y-1"
                      >
                        <div className="flex justify-between font-semibold text-[#323F36]">
                          <span>{c.claim_code} • {c.source_name}</span>
                          <span className="font-mono text-[10px] text-[#5E6F63]">{c.line_span}</span>
                        </div>
                        <div className="text-[#222B25] font-mono italic">
                          "{c.exact_quote}"
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Redaction Notice */}
              {msg.redactedCount > 0 && (
                <div className="p-2 rounded-lg bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF] text-[11px] flex items-center space-x-1.5">
                  <Lock className="w-3.5 h-3.5 shrink-0" />
                  <span>{msg.redactedCount} related confidential item(s) hidden under DLP policy.</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="p-4 rounded-2xl bg-white border border-[#E5D5BF] text-xs text-[#8B968D] flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-[#4E5D52] animate-ping" />
              <span>Synthesizing evidence-backed response from immutable ledger...</span>
            </div>
          </div>
        )}
      </div>

      {/* Sample Query Suggestions */}
      <div className="py-2 flex flex-wrap gap-1.5 overflow-x-auto shrink-0">
        {sampleQuestions.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            className="text-[11px] px-2.5 py-1 rounded-lg border border-[#E5D5BF] bg-white text-[#4E5D52] hover:bg-[#FAF5EE] transition-colors shrink-0"
          >
            "{q}"
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="pt-2 flex space-x-2 shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a technical or operational question (e.g. 'Why was pgvector chosen over DynamoDB?')..."
          className="flex-1 p-3 rounded-xl border border-[#E5D5BF] bg-white text-xs text-[#222B25] focus:outline-hidden focus:ring-2 focus:ring-[#4E5D52] shadow-2xs"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading}
          className="py-3 px-5 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5"
        >
          <Send className="w-4 h-4" />
          <span className="hidden sm:inline">Ask AI</span>
        </button>
      </div>
    </div>
  );
}
