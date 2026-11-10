"use client";

import React, { useState, useEffect } from "react";
import {
  HelpCircle,
  MessageSquare,
  CheckCircle2,
  Send,
  Plus,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export function KnowledgeGapsView() {
  const { currentProject, user } = useAuth();
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeQuestion, setActiveQuestion] = useState<any | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [answering, setAnswering] = useState(false);
  const [showNewQModal, setShowNewQModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState("");
  const [newRationale, setNewRationale] = useState("");

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const res = await api.getGapQuestions({ projectId: currentProject.id });
      setQuestions(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [currentProject]);

  const handleAnswer = async () => {
    if (!activeQuestion || !answerText.trim()) return;
    setAnswering(true);
    try {
      await api.answerGapQuestion(activeQuestion.id, {
        answer: answerText,
        respondent_name: user?.full_name || "Sarah Lin",
      });
      fetchQuestions();
      setActiveQuestion(null);
      setAnswerText("");
      alert("Clarification answer recorded and tagged to handover ledger!");
    } catch (e) {
      console.error(e);
    } finally {
      setAnswering(false);
    }
  };

  const handleCreateQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion.trim()) return;
    try {
      await api.createGapQuestion({
        project_id: currentProject.id,
        question: newQuestion,
        rationale: newRationale,
        target_user_name: "Sarah Lin (Departing Staff)",
      });
      fetchQuestions();
      setShowNewQModal(false);
      setNewQuestion("");
      setNewRationale("");
    } catch (err) {
      console.error(err);
    }
  };

  const openCount = questions.filter((q) => q.status === "Open").length;

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 max-w-6xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5D5BF] pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-[#222B25]">
              Targeted Knowledge Gap Questions
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]">
              {openCount} Awaiting Clarification
            </span>
          </div>
          <p className="text-xs text-[#5E6F63] mt-1">
            AI-identified ambiguities automatically converted into directed inquiries for departing leads.
          </p>
        </div>

        <button
          onClick={() => setShowNewQModal(true)}
          className="py-2 px-3.5 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Ask Gap Question</span>
        </button>
      </div>

      {/* Questions Stream */}
      <div className="space-y-4">
        {questions.map((q) => {
          const isAnswered = q.status === "Answered";
          return (
            <div
              key={q.id}
              className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#8B968D] font-medium">
                  Directed to: <strong className="text-[#222B25]">{q.target_user_name}</strong>
                </span>
                <span
                  className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${
                    isAnswered
                      ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                      : "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
                  }`}
                >
                  {q.status}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-[#222B25] leading-snug">
                  {q.question}
                </h3>
                {q.rationale && (
                  <p className="text-xs text-[#5E6F63] mt-1">
                    <span className="font-semibold text-[#222B25]">Context:</span> {q.rationale}
                  </p>
                )}
              </div>

              {/* Clarification Answer Box if answered */}
              {isAnswered && (
                <div className="p-3.5 rounded-xl bg-[#EFF3ED] border border-[#A6B29C] text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-semibold text-[#323F36]">
                    <span className="flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#4E5D52]" />
                      <span>Clarification by {q.respondent_name}</span>
                    </span>
                    <span className="font-mono text-[10px]">
                      {new Date(q.answered_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-[#222B25] leading-relaxed font-sans pt-1">
                    "{q.answer}"
                  </p>
                  <div className="text-[10px] text-[#8B968D] font-mono pt-1">
                    Distinguishable from source-derived code evidence.
                  </div>
                </div>
              )}

              {/* Action button if open */}
              {!isAnswered && (
                <div className="pt-2">
                  <button
                    onClick={() => setActiveQuestion(q)}
                    className="py-1.5 px-3 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-2xs transition-colors flex items-center space-x-1.5"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Provide Clarification Answer</span>
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Answer Modal */}
      {activeQuestion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl p-6 space-y-4">
            <h3 className="font-bold text-sm text-[#222B25]">
              Answer Knowledge Gap Inquiry
            </h3>
            <p className="text-xs text-[#5E6F63] font-medium">
              "{activeQuestion.question}"
            </p>

            <div>
              <label className="text-xs font-semibold text-[#222B25]">
                Authoritative Clarification:
              </label>
              <textarea
                rows={4}
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Explain the technical or business rationale..."
                className="mt-1 w-full p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25] focus:outline-hidden focus:ring-2 focus:ring-[#4E5D52]"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setActiveQuestion(null)}
                className="py-2 px-3 rounded-xl border border-[#E5D5BF] text-xs font-medium text-[#5E6F63]"
              >
                Cancel
              </button>
              <button
                onClick={handleAnswer}
                disabled={answering || !answerText.trim()}
                className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold"
              >
                {answering ? "Recording..." : "Record Clarification"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Question Modal */}
      {showNewQModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl p-6 space-y-4">
            <h3 className="font-bold text-sm text-[#222B25]">
              Create Knowledge Gap Inquiry
            </h3>
            <form onSubmit={handleCreateQuestion} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-[#222B25]">
                  Question:
                </label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="e.g. Why was the authentication module not completed?"
                  className="mt-1 w-full p-2.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25]"
                />
              </div>
              <div>
                <label className="font-semibold text-[#222B25]">
                  Context / Rationale:
                </label>
                <textarea
                  rows={2}
                  value={newRationale}
                  onChange={(e) => setNewRationale(e.target.value)}
                  placeholder="e.g. Unmerged branch in GitHub lacks documentation..."
                  className="mt-1 w-full p-2.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25]"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewQModal(false)}
                  className="py-2 px-3 rounded-xl border border-[#E5D5BF] text-[#5E6F63]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white font-semibold"
                >
                  Submit Inquiry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
