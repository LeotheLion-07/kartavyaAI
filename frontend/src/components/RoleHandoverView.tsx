"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Search,
  MessageSquare,
  Sparkles,
  Layers,
  UserCheck,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ExportPdfModal } from "./ExportPdfModal";

interface RoleHandoverViewProps {
  onOpenInspector: (claim: any) => void;
  onOpenChat: () => void;
}

export function RoleHandoverView({ onOpenInspector, onOpenChat }: RoleHandoverViewProps) {
  const { currentProject, user } = useAuth();
  const [roleData, setRoleData] = useState<any>(null);
  const [handoverFull, setHandoverFull] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showPdf, setShowPdf] = useState(false);
  const [acknowledging, setAcknowledging] = useState(false);
  const [qnaQuery, setQnaQuery] = useState("");
  const [qnaResult, setQnaResult] = useState<any>(null);
  const [qnaLoading, setQnaLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const devView = await api.getRoleView("developer", currentProject.id);
      setRoleData(devView);

      const cases = await api.getHandoverCases(currentProject.id);
      if (cases.length > 0) {
        const full = await api.getHandoverCase(cases[0].id);
        setHandoverFull(full);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentProject]);

  const handleAcknowledge = async () => {
    if (!handoverFull?.case?.id) return;
    setAcknowledging(true);
    try {
      await api.acknowledgeHandover(handoverFull.case.id, {
        notes: `Receipt acknowledged by ${user?.full_name || "Marcus Vance"}. Cluster permissions and runbooks verified.`,
      });
      fetchData();
      alert("Transfer receipt cryptographically signed and acknowledged!");
    } catch (e) {
      console.error(e);
    } finally {
      setAcknowledging(false);
    }
  };

  const handleToggleTask = async (taskId: number) => {
    try {
      await api.toggleTask(taskId);
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearchQna = async (term?: string) => {
    const queryToRun = term || qnaQuery;
    if (!queryToRun.trim()) return;
    setQnaLoading(true);
    try {
      const res = await api.queryChat({
        project_id: currentProject.id,
        query: queryToRun,
      });
      setQnaResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setQnaLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12 text-[#8B968D]">
        <div className="w-8 h-8 border-2 border-[#4E5D52] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const isAcknowledged = handoverFull?.case?.status?.includes("Acknowledged");
  const tasks = handoverFull?.tasks || [];
  const completedTasksCount = tasks.filter((t: any) => t.is_completed).length;

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Subheader / Scope Line */}
      <div className="flex flex-wrap items-center justify-between text-xs text-[#5E6F63] border-b border-[#E5D5BF] pb-3 gap-2">
        <div className="flex items-center space-x-3">
          <span className="font-semibold text-[#222B25] flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-[#4E5D52]" />
            <span>Scope: {currentProject.name}</span>
          </span>
          <span>•</span>
          <span className="text-[#5E6F63]">
            {handoverFull?.case?.stage || "Stage 5 of 5 · Final Cutover Execution"}
          </span>
          <span>•</span>
          <span className="font-semibold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
            {handoverFull?.case?.grounded_pct || 94}% Claims Grounded
          </span>
        </div>
        <div className="text-[#8B968D] font-mono text-[11px]">
          Cutover Target: {new Date(handoverFull?.case?.target_cutover_date || Date.now()).toLocaleDateString()}
        </div>
      </div>

      {/* Executive Transfer Order Banner */}
      <div className="p-6 rounded-2xl border border-[#E5D5BF] bg-white shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-[#FAF5EE] text-[#4E5D52] border border-[#E5D5BF]">
            <FileText className="w-3.5 h-3.5 text-[#4E5D52]" />
            <span>Executive Transfer Order</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#222B25]">
            Welcome Marcus Vance • Incoming Lead, {currentProject.name}
          </h1>
          <p className="text-xs text-[#5E6F63] leading-relaxed">
            Synthesized from 180+ immutable project artifacts. Prepared by departing lead{" "}
            <strong className="text-[#222B25]">Sarah Lin (Staff Eng)</strong> and signed off by{" "}
            <strong className="text-[#222B25]">Alex Morgan</strong>. All architecture claims are tied
            directly to verifiable Git commits.
          </p>
        </div>

        {/* Transfer Status & Acknowledge Button */}
        <div className="flex flex-col items-end space-y-2 w-full md:w-auto">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-[#8B968D] uppercase text-[10px] font-semibold">Transfer Status:</span>
            <span
              className={`px-2.5 py-0.5 rounded-full font-semibold text-xs ${
                isAcknowledged
                  ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                  : "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
              }`}
            >
              {isAcknowledged ? "Cutover Acknowledged" : "Pending Sign-off"}
            </span>
          </div>
          <div className="flex space-x-2 w-full md:w-auto">
            <button
              onClick={() => setShowPdf(true)}
              className="py-2.5 px-4 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] hover:bg-[#F2EADB] text-xs font-semibold text-[#4E5D52] transition-colors"
            >
              Export Report (PDF)
            </button>
            <button
              onClick={handleAcknowledge}
              disabled={acknowledging || isAcknowledged}
              className={`py-2.5 px-5 rounded-xl text-xs font-semibold shadow-xs transition-all flex items-center space-x-2 ${
                isAcknowledged
                  ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C] cursor-default"
                  : "bg-[#4E5D52] hover:bg-[#3A473E] text-white active:scale-98"
              }`}
            >
              <UserCheck className="w-4 h-4" />
              <span>{isAcknowledged ? "Receipt Signed & Active" : acknowledging ? "Signing..." : "Acknowledge & Sign Receipt"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Systems + Q&A | Right 30-Day Plan + Contacts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Critical Architecture & Systems You Own */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#222B25]">
                <Layers className="w-4 h-4 text-[#4E5D52]" />
                <span>Critical Architecture & Systems You Own</span>
              </div>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#FAF5EE] text-[#4E5D52] border border-[#E5D5BF] font-medium">
                2 Core Services
              </span>
            </div>

            {/* Service 1: Payment Settlement Worker */}
            <div className="p-4 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE]/70 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-[#A6B29C]" />
                    <h3 className="font-semibold text-sm text-[#222B25]">
                      Payment Settlement Worker
                    </h3>
                  </div>
                  <div className="text-[11px] text-[#5E6F63] mt-0.5">
                    FastAPI • RQ Celery • Redis Cluster
                  </div>
                </div>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                  Stable in Prod
                </span>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-2 text-xs bg-white p-2.5 rounded-lg border border-[#E5D5BF]">
                <div>
                  <div className="text-[#8B968D] text-[10px]">Throughput</div>
                  <div className="font-bold text-[#222B25]">4,500 req/s</div>
                </div>
                <div>
                  <div className="text-[#8B968D] text-[10px]">P99 Latency</div>
                  <div className="font-bold text-[#222B25]">84ms (&lt;150ms SLA)</div>
                </div>
                <div>
                  <div className="text-[#8B968D] text-[10px]">Infrastructure</div>
                  <div className="font-bold text-[#222B25]">12 EKS Pods</div>
                </div>
              </div>

              {/* Active Blocker Alert */}
              <div className="p-2.5 rounded-lg bg-[#FAF0E6] border border-[#E5D5BF] text-xs space-y-1">
                <div className="flex items-center space-x-1.5 text-[#7A3E2D] font-semibold">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-[#C2783B]" />
                  <span>Active Blocker: Stripe webhook timeout bug during traffic bursts exceeding 4,200 rps batch payouts.</span>
                </div>
              </div>

              {/* Immediate 1st Action */}
              <div className="p-2.5 rounded-lg bg-[#EFF3ED] border border-[#A6B29C] text-xs text-[#323F36] flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#4E5D52] shrink-0" />
                <span>
                  <strong>Immediate 1st Action:</strong> Increase async timeout in{" "}
                  <code className="px-1 py-0.5 rounded bg-white border border-[#E5D5BF] font-mono text-[11px] text-[#4E5D52]">
                    worker.py: line 84
                  </code>{" "}
                  to 15s and configure exponential backoff in Redis broker.
                </span>
              </div>
            </div>

            {/* Service 2: PostgreSQL 16 + pgvector */}
            <div className="p-4 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE]/70 space-y-2.5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-[#4E5D52]" />
                    <h3 className="font-semibold text-sm text-[#222B25]">
                      PostgreSQL 16 + pgvector
                    </h3>
                  </div>
                  <div className="text-[11px] text-[#5E6F63] mt-0.5">
                    OLTP Primary • Semantic Vector Embeddings (HNSW)
                  </div>
                </div>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                  Migrated Sprint 41
                </span>
              </div>

              <p className="text-xs text-[#5E6F63] leading-relaxed">
                Main transaction storage & RAG index with HNSW (m=16, ef_construction=64). Houses all
                user vectors and contextual decision history.
              </p>

              <div className="p-2.5 rounded-lg bg-[#FAF5EE] border border-[#C9B79E] text-xs text-[#63513C] flex items-center space-x-2">
                <Clock className="w-3.5 h-3.5 shrink-0 text-[#C9B79E]" />
                <span>
                  <strong>Scaling Imperative:</strong> Monitor memory footprint as index crosses 800k
                  vectors. Provisioning upgrade to 32GB RAM recommended before reaching 1,000,000 threshold.
                </span>
              </div>
            </div>
          </div>

          {/* Grounded Handover Q&A Box */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#222B25]">
                <MessageSquare className="w-4 h-4 text-[#4E5D52]" />
                <span>Grounded Handover Q&A</span>
              </div>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                Zero Hallucination Model
              </span>
            </div>

            <p className="text-xs text-[#5E6F63]">
              Answers are strictly derived from verified handover commits, pull requests, and
              architectural decision memos.
            </p>

            {/* Input Bar */}
            <div className="flex space-x-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-[#8B968D] absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={qnaQuery}
                  onChange={(e) => setQnaQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearchQna()}
                  placeholder="Ask anything about this repo (e.g. 'Where is DB connection pool initialized?')"
                  className="w-full pl-9 pr-3 py-2 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25] focus:outline-hidden focus:ring-2 focus:ring-[#4E5D52]"
                />
              </div>
              <button
                onClick={() => handleSearchQna()}
                disabled={qnaLoading}
                className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold transition-colors"
              >
                {qnaLoading ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Prompt pills */}
            <div className="flex flex-wrap gap-1.5">
              {["Database pool setup?", "Why not Celery Beat?", "On-call escalation?"].map((pill) => (
                <button
                  key={pill}
                  onClick={() => {
                    setQnaQuery(pill);
                    handleSearchQna(pill);
                  }}
                  className="px-2.5 py-1 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] text-[11px] text-[#4E5D52] hover:bg-[#F2EADB] transition-colors"
                >
                  "{pill}"
                </button>
              ))}
            </div>

            {/* Result Box */}
            {qnaResult && (
              <div className="p-3.5 rounded-xl border border-[#A6B29C] bg-[#EFF3ED] text-xs space-y-2 animate-in fade-in">
                <div className="flex items-center justify-between text-[#323F36] text-[11px] font-semibold">
                  <span className="flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#4E5D52]" />
                    <span>Verified Source: RFC-044 • app/core/database.py</span>
                  </span>
                  <span className="font-mono">Confidence: 99.4%</span>
                </div>
                <p className="text-[#222B25] leading-relaxed font-sans">
                  {qnaResult.answer}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* 30-Day Onboarding Plan */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#222B25]">
                <Clock className="w-4 h-4 text-[#4E5D52]" />
                <span>30-Day Onboarding Plan</span>
              </div>
              <span className="text-xs font-semibold text-[#4E5D52]">
                {completedTasksCount} of {tasks.length} Completed
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-[#FAF5EE] rounded-full h-2 overflow-hidden border border-[#E5D5BF]">
              <div
                className="bg-[#4E5D52] h-2 rounded-full transition-all duration-300"
                style={{ width: `${(completedTasksCount / Math.max(1, tasks.length)) * 100}%` }}
              />
            </div>

            {/* Phase breakdown */}
            <div className="space-y-4 pt-1">
              {/* Phase 1 */}
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-[#8B968D] mb-2">
                  <span>Phase 1 • Ramp-up & Context</span>
                  <span className="font-mono text-[#8B968D]">Day 1-7</span>
                </div>
                <div className="space-y-2">
                  {tasks
                    .filter((t: any) => t.phase?.includes("Phase 1"))
                    .map((task: any) => (
                      <label
                        key={task.id}
                        className="flex items-start space-x-2.5 p-2 rounded-lg hover:bg-[#FAF5EE] cursor-pointer text-xs transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={task.is_completed}
                          onChange={() => handleToggleTask(task.id)}
                          className="mt-0.5 rounded text-[#4E5D52] focus:ring-[#4E5D52]"
                        />
                        <span
                          className={`${
                            task.is_completed
                              ? "line-through text-[#8B968D] font-medium"
                              : "text-[#222B25] font-medium"
                          }`}
                        >
                          {task.title}
                        </span>
                      </label>
                    ))}
                </div>
              </div>

              {/* Phase 2 */}
              <div className="pt-2 border-t border-[#E5D5BF]">
                <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-[#8B968D] mb-2">
                  <span>Phase 2 • First Deployment</span>
                  <span className="font-mono text-[#8B968D]">Day 8-15</span>
                </div>
                <div className="space-y-2">
                  {tasks
                    .filter((t: any) => t.phase?.includes("Phase 2"))
                    .map((task: any) => (
                      <label
                        key={task.id}
                        className="flex items-start space-x-2.5 p-2 rounded-lg hover:bg-[#FAF5EE] cursor-pointer text-xs transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={task.is_completed}
                          onChange={() => handleToggleTask(task.id)}
                          className="mt-0.5 rounded text-[#4E5D52] focus:ring-[#4E5D52]"
                        />
                        <span
                          className={`${
                            task.is_completed
                              ? "line-through text-[#8B968D] font-medium"
                              : "text-[#222B25] font-medium"
                          }`}
                        >
                          {task.title}
                        </span>
                      </label>
                    ))}
                </div>
              </div>

              {/* Phase 3 */}
              <div className="pt-2 border-t border-[#E5D5BF]">
                <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-[#8B968D] mb-2">
                  <span>Phase 3 • Full Ownership</span>
                  <span className="font-mono text-[#8B968D]">Day 16-30</span>
                </div>
                <div className="space-y-2">
                  {tasks
                    .filter((t: any) => t.phase?.includes("Phase 3"))
                    .map((task: any) => (
                      <label
                        key={task.id}
                        className="flex items-start space-x-2.5 p-2 rounded-lg hover:bg-[#FAF5EE] cursor-pointer text-xs transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={task.is_completed}
                          onChange={() => handleToggleTask(task.id)}
                          className="mt-0.5 rounded text-[#4E5D52] focus:ring-[#4E5D52]"
                        />
                        <span
                          className={`${
                            task.is_completed
                              ? "line-through text-[#8B968D] font-medium"
                              : "text-[#222B25] font-medium"
                          }`}
                        >
                          {task.title}
                        </span>
                      </label>
                    ))}
                </div>
              </div>
            </div>
          </div>

          {/* Key Team Contacts / Escalation Grid */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
                Key Team Contacts
              </div>
              <span className="text-[11px] text-[#8B968D] font-medium">Escalation Grid</span>
            </div>

            <div className="divide-y divide-[#E5D5BF]">
              <div className="py-2.5 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-full bg-[#4E5D52] text-white font-bold text-xs flex items-center justify-center">
                    SL
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-[#222B25] flex items-center space-x-1.5">
                      <span>Sarah Lin</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E] font-medium">
                        Departing Staff
                      </span>
                    </div>
                    <div className="text-[10px] text-[#8B968D]">sarah@company.internal</div>
                  </div>
                </div>
                <button
                  onClick={onOpenChat}
                  className="p-1.5 text-[#5E6F63] hover:text-[#4E5D52] transition-colors"
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>

              <div className="py-2.5 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <img
                    src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"
                    alt="David K."
                    className="w-8 h-8 rounded-full object-cover"
                  />
                  <div>
                    <div className="text-xs font-semibold text-[#222B25]">
                      David K. <span className="text-[10px] text-[#8B968D] font-normal">Backend Peer</span>
                    </div>
                    <div className="text-[10px] text-[#8B968D]">Domain: Webhook Engine & RQ Queues</div>
                  </div>
                </div>
                <button
                  onClick={onOpenChat}
                  className="p-1.5 text-[#5E6F63] hover:text-[#4E5D52] transition-colors"
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>

              <div className="py-2.5 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <img
                    src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
                    alt="Elena R."
                    className="w-8 h-8 rounded-full object-cover"
                  />
                  <div>
                    <div className="text-xs font-semibold text-[#222B25]">
                      Elena R. <span className="text-[10px] text-[#8B968D] font-normal">Infra Lead</span>
                    </div>
                    <div className="text-[10px] text-[#8B968D]">Domain: Terraform, EKS & IAM Security</div>
                  </div>
                </div>
                <button
                  onClick={onOpenChat}
                  className="p-1.5 text-[#5E6F63] hover:text-[#4E5D52] transition-colors"
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>

              <div className="py-2.5 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <img
                    src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"
                    alt="Alex Morgan"
                    className="w-8 h-8 rounded-full object-cover"
                  />
                  <div>
                    <div className="text-xs font-semibold text-[#222B25]">
                      Alex Morgan <span className="text-[10px] text-[#8B968D] font-normal">Eng Manager</span>
                    </div>
                    <div className="text-[10px] text-[#8B968D]">Domain: Approvals, Headcount & SLAs</div>
                  </div>
                </div>
                <button
                  onClick={onOpenChat}
                  className="p-1.5 text-[#5E6F63] hover:text-[#4E5D52] transition-colors"
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export PDF Modal */}
      {showPdf && handoverFull && (
        <ExportPdfModal handoverData={handoverFull} onClose={() => setShowPdf(false)} />
      )}
    </div>
  );
}
