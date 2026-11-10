"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Lock,
  GitPullRequest,
  Check,
  ArrowRight,
  ExternalLink,
  Sparkles,
  Printer,
  History,
  Clock,
  UserCheck,
  FileText,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ConflictResolutionModal } from "./ConflictResolutionModal";
import { ExportPdfModal } from "./ExportPdfModal";

interface EvidenceBoardViewProps {
  onOpenConflictModal: () => void;
}

export function EvidenceBoardView({ onOpenConflictModal }: EvidenceBoardViewProps) {
  const { currentProject, user } = useAuth();
  const [handoverData, setHandoverData] = useState<any>(null);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [selectedConflict, setSelectedConflict] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [authorizing, setAuthorizing] = useState(false);
  const [showPdf, setShowPdf] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const cases = await api.getHandoverCases(currentProject.id);
      if (cases.length > 0) {
        const full = await api.getHandoverCase(cases[0].id);
        setHandoverData(full);
      }
      const confList = await api.getConflicts({ projectId: currentProject.id });
      setConflicts(confList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentProject]);

  const handleAuthorizeCutover = async () => {
    if (!handoverData?.case?.id) return;
    setAuthorizing(true);
    try {
      await api.approveHandover(handoverData.case.id);
      fetchData();
      alert("Transition package authorized and cryptographically signed by Alex Morgan!");
    } catch (e) {
      console.error(e);
    } finally {
      setAuthorizing(false);
    }
  };

  const pendingConflict = conflicts.find((c) => c.resolution_status === "Pending");
  const isConflictResolved = !pendingConflict;
  const isPublished = handoverData?.case?.status?.includes("Cutover Authorized") || handoverData?.case?.status?.includes("Acknowledged");

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Top Meta Line */}
      <div className="flex flex-wrap items-center justify-between text-xs text-[#5E6F63] border-b border-[#E5D5BF] pb-3 gap-2">
        <div className="flex items-center space-x-3">
          <span className="font-mono font-bold text-[#4E5D52]">
            {handoverData?.case?.case_number || "CASE-2024-884A"}
          </span>
          <span>•</span>
          <span className="text-[#5E6F63]">
            Stage 4: Sign-off & Verification
          </span>
        </div>
        <div className="text-[#8B968D] font-mono text-[11px]">
          Target Cutover: Oct 28, 2024 (17:00 UTC)
        </div>
      </div>

      {/* Main Title & Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#222B25]">
            Core Platform & Payment Gateway Transition
          </h1>
          <p className="text-xs text-[#5E6F63] mt-1">
            Sarah Lin (Staff Lead L6) → Marcus Vance (Senior L5 Successor)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => alert("15-Min Exit Sync call joined via Google Meet.")}
            className="py-2 px-3.5 rounded-xl border border-[#E5D5BF] bg-white hover:bg-[#FAF5EE] text-xs font-semibold text-[#4E5D52] flex items-center space-x-1.5 transition-colors shadow-2xs"
          >
            <span>15-Min Exit Sync</span>
          </button>
          <button
            onClick={() => setShowPdf(true)}
            className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Approve & Publish Handover</span>
          </button>
        </div>
      </div>

      {/* Participant Status Badges */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Sarah Lin Badge */}
        <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img
              src="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150"
              alt="Sarah Lin"
              className="w-9 h-9 rounded-full object-cover ring-2 ring-[#A6B29C]"
            />
            <div>
              <div className="text-xs font-bold text-[#222B25]">
                Sarah Lin <span className="text-[11px] text-[#8B968D] font-normal">(Departing Lead)</span>
              </div>
              <div className="text-[11px] text-[#5E6F63]">Signed & Verified on Oct 24, 14:12 UTC</div>
            </div>
          </div>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C] flex items-center space-x-1">
            <Check className="w-3.5 h-3.5" />
            <span>Approved</span>
          </span>
        </div>

        {/* Alex Morgan Badge */}
        <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img
              src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"
              alt="Alex Morgan"
              className="w-9 h-9 rounded-full object-cover ring-2 ring-[#4E5D52]"
            />
            <div>
              <div className="text-xs font-bold text-[#222B25]">
                Alex Morgan <span className="text-[11px] text-[#8B968D] font-normal">(Engineering Manager)</span>
              </div>
              <div className="text-[11px] text-[#5E6F63]">
                {isConflictResolved ? "Gate criteria satisfied" : "1 Conflict to resolve before publication"}
              </div>
            </div>
          </div>
          <button
            onClick={handleAuthorizeCutover}
            className={`text-xs font-bold px-3 py-1 rounded-full transition-colors ${
              isPublished
                ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                : "bg-[#4E5D52] hover:bg-[#3A473E] text-white"
            }`}
          >
            {isPublished ? "Authorized" : "Sign Off Now"}
          </button>
        </div>
      </div>

      {/* Main Grid: Left Handover Doc & Conflict | Right Manager Gate & Evidence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Unresolved Ambiguity / Conflict Card */}
          <div className="p-5 rounded-2xl border border-[#C9B79E] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-bold text-[#63513C] uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-[#C9B79E] animate-ping" />
                <span>Unresolved Ambiguity • Conflict #882</span>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                isConflictResolved
                  ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                  : "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
              }`}>
                {isConflictResolved ? "Resolved" : "Action Required"}
              </span>
            </div>

            <div>
              <h3 className="text-sm font-bold text-[#222B25]">
                Webhook Failover Circuit Breaker Ownership Discrepancy
              </h3>
              <p className="text-xs text-[#5E6F63] mt-1 leading-relaxed">
                Two canonical systems assign differing primary on-call tiers for the Stripe & Adyen webhook reconciliation pipeline. This creates critical operational ambiguity for the successor during an outage.
              </p>
            </div>

            {/* Side-by-side sources */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs space-y-2">
                <div className="flex justify-between text-[10px] text-[#8B968D]">
                  <span className="font-semibold text-[#222B25]">Codebase PR #1420</span>
                  <span>Sep 12</span>
                </div>
                <div className="font-mono text-[11px] text-[#222B25] bg-white p-2 rounded border border-[#E5D5BF] italic">
                  // circuit_breaker.go: line 104<br />
                  // Delegated to Core Infra SRE<br />
                  circuit.Notify("pagerduty:core-sre");
                </div>
                <div className="text-[11px] text-[#63513C] font-medium">
                  Claim: Core Infra SRE owns manual overrides
                </div>
              </div>

              <div className="p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs space-y-2">
                <div className="flex justify-between text-[10px] text-[#8B968D]">
                  <span className="font-semibold text-[#222B25]">Arch Sync Notes (Slack)</span>
                  <span>Oct 04</span>
                </div>
                <div className="font-mono text-[11px] text-[#222B25] bg-white p-2 rounded border border-[#E5D5BF] italic">
                  "Sarah agreed Payments Pod owns manual drain triggers until Q1-25. SRE only receives metric pings."
                </div>
                <div className="text-[11px] text-[#4E5D52] font-medium">
                  Claim: Payments Pod (Marcus) retains override triggers
                </div>
              </div>
            </div>

            {/* Recommended Fix Box & Action */}
            <div className="p-3.5 rounded-xl border border-[#A6B29C] bg-[#EFF3ED] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="text-[#323F36]">
                <span className="font-bold">Recommended Fix:</span> Assign Payments Pod L2 triage; SRE retains automated restart without raw API tokens.
              </div>
              <div className="flex space-x-2 shrink-0">
                <button
                  onClick={() => setSelectedConflict(conflicts[0] || { id: 1, conflict_code: "CONF-882", title: "Webhook Circuit Breaker Ownership", description: "Discrepancy between PR and Slack" })}
                  className="py-1.5 px-3 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white font-semibold transition-colors shadow-2xs"
                >
                  Accept Resolution
                </button>
                <button
                  onClick={() => alert("15-Min Exit sync requested.")}
                  className="py-1.5 px-3 rounded-lg border border-[#E5D5BF] bg-white text-[#4E5D52] hover:bg-[#FAF5EE] text-xs font-medium"
                >
                  15-min Exit Sync
                </button>
              </div>
            </div>
          </div>

          {/* Synthesized Handover Document */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-[#4E5D52]" />
                <span>Synthesized Handover Document</span>
              </div>
              <span className="text-[11px] font-mono text-[#8B968D] font-medium">
                v2.4 Final Draft
              </span>
            </div>

            <div className="space-y-3 text-xs leading-relaxed text-[#5E6F63]">
              <h3 className="font-bold text-sm text-[#222B25]">
                1. Payment Ingestion Architecture & Failure Modes
              </h3>
              <p className="text-[11px] text-[#8B968D]">
                Anchored by 24 commits, 8 GitHub PRs, and verified Slack sync records.
              </p>

              <p>
                The primary transaction pipeline relies on asynchronous double-dispatch via Kafka topic{" "}
                <code className="px-1 py-0.5 rounded bg-[#FAF5EE] border border-[#E5D5BF] font-mono text-[#4E5D52]">
                  payments.events.settlement.v2
                </code>
                . Under peak loads exceeding 4,500 TPS, backpressure mitigation shifts buffering to the
                secondary Redis cluster. <span className="inline-block px-1.5 py-0.2 rounded bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C] text-[10px] font-semibold">#PR-1420</span> All payloads undergo idempotent schema verification prior to immutable ledger write.
              </p>

              {/* Failover Switch Routine with REDACTED token */}
              <div className="p-3.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] space-y-2">
                <div className="flex items-center space-x-1.5 text-[#222B25] font-semibold text-xs">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#4E5D52]" />
                  <span>Failover Switch Routine (Adyen → Stripe Direct)</span>
                </div>
                <div className="text-[11px] text-[#8B968D]">
                  If the Adyen primary gateway returns consecutive 504 timeouts for &gt;45 seconds, the system shifts traffic autonomously.
                </div>
                <div className="p-2.5 rounded-lg bg-[#28322B] font-mono text-[11px] text-[#EFF3ED] border border-[#3A473E]">
                  ./bin/payctl circuit reset --gateway=adyen --force-token=<span className="text-[#C9B79E] font-bold">[REDACTED_VAULT_KEY]</span>
                </div>
              </div>

              <p>
                Marcus Vance has been provisioned Okta group privileges for{" "}
                <code className="font-mono text-[#222B25]">eng-payments-oncall</code>.
                Secondary AWS breakglass credentials will deploy automatically upon final manager sign-off.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Manager Gate */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
                Manager Gate
              </div>
              <span className="text-xs font-semibold text-[#4E5D52]">
                {isConflictResolved ? "4 of 4 Ready" : "3 of 4 Ready"}
              </span>
            </div>

            <div className="space-y-3">
              {/* Gate Item 1 */}
              <div className="flex items-start space-x-2.5 text-xs">
                <div className="w-4 h-4 rounded bg-[#4E5D52] text-white flex items-center justify-center text-[10px] mt-0.5">
                  ✓
                </div>
                <div>
                  <div className="font-semibold text-[#222B25]">
                    All claims backed by citations
                  </div>
                  <div className="text-[11px] text-[#8B968D]">24 of 24 PRs and docs validated</div>
                </div>
              </div>

              {/* Gate Item 2 */}
              <div className="flex items-start space-x-2.5 text-xs">
                <div className="w-4 h-4 rounded bg-[#4E5D52] text-white flex items-center justify-center text-[10px] mt-0.5">
                  ✓
                </div>
                <div>
                  <div className="font-semibold text-[#222B25]">
                    No hallucinated assertions
                  </div>
                  <div className="text-[11px] text-[#8B968D]">Zero ungrounded text in v2.4</div>
                </div>
              </div>

              {/* Gate Item 3 */}
              <div className="flex items-start space-x-2.5 text-xs">
                <div className="w-4 h-4 rounded bg-[#4E5D52] text-white flex items-center justify-center text-[10px] mt-0.5">
                  ✓
                </div>
                <div>
                  <div className="font-semibold text-[#222B25]">
                    Credentials & SLAs Redacted
                  </div>
                  <div className="text-[11px] text-[#8B968D]">DLP mask applied to Stripe live token</div>
                </div>
              </div>

              {/* Gate Item 4 (Conflict) */}
              <div className="flex items-start space-x-2.5 text-xs">
                <div
                  className={`w-4 h-4 rounded flex items-center justify-center text-[10px] mt-0.5 ${
                    isConflictResolved ? "bg-[#4E5D52] text-white" : "border border-[#C9B79E]"
                  }`}
                >
                  {isConflictResolved ? "✓" : ""}
                </div>
                <div>
                  <div className="font-semibold text-[#222B25]">
                    Conflict #882 Resolved
                  </div>
                  <div className={`text-[11px] ${isConflictResolved ? "text-[#323F36]" : "text-[#63513C]"}`}>
                    {isConflictResolved ? "Resolved by Alex Morgan" : "Pending resolution above"}
                  </div>
                </div>
              </div>
            </div>

            {/* Authorize Cutover Button */}
            <div className="pt-2">
              <button
                onClick={handleAuthorizeCutover}
                disabled={authorizing || !isConflictResolved}
                className={`w-full py-2.5 px-4 rounded-xl text-xs font-semibold shadow-xs transition-all flex items-center justify-center space-x-2 ${
                  isConflictResolved
                    ? "bg-[#4E5D52] hover:bg-[#3A473E] text-white"
                    : "bg-[#FAF5EE] text-[#8B968D] border border-[#E5D5BF] cursor-not-allowed"
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                <span>
                  {isPublished
                    ? "Cutover Authorized (Package Signed)"
                    : authorizing
                    ? "Authorizing..."
                    : "Authorize Cutover to Marcus"}
                </span>
              </button>
              <div className="text-[10px] text-[#8B968D] text-center mt-1.5 font-mono">
                Cryptographically signs the transition package v2.4
              </div>
            </div>
          </div>

          {/* Evidence Grounding Diff */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-1.5">
                <GitPullRequest className="w-3.5 h-3.5 text-[#4E5D52]" />
                <span>Evidence Grounding</span>
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                Verified
              </span>
            </div>

            <div className="text-xs">
              <div className="font-mono text-[#4E5D52] font-semibold">#PR-1420</div>
              <div className="text-[11px] text-[#5E6F63]">
                feat(core): Kafka dual-dispatch partition failover
              </div>
              <div className="text-[10px] text-[#8B968D] mt-0.5">
                Author: Sarah Lin • Reviewer: Marcus Vance
              </div>
            </div>

            <pre className="p-3 rounded-xl bg-[#28322B] text-[#EFF3ED] text-[11px] font-mono overflow-x-auto border border-[#3A473E]">
              <code>{`+ func DispatchWithBackpressure(ctx context.Context, msg)
+   if broker.QueueDepth() > 4500 {
+     return redisFallback.Store(ctx, msg)
+   }
+   return broker.Publish("payments.events.settlement.v2", msg)`}</code>
            </pre>

            <div className="flex justify-between items-center text-[10px] text-[#8B968D] pt-1">
              <span>Commit: 9b2ff07</span>
              <a href="https://github.com" target="_blank" className="text-[#4E5D52] hover:underline font-semibold">
                Open in GitHub →
              </a>
            </div>
          </div>

          {/* Handover Audit Lineage */}
          <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
              Handover Audit Lineage
            </div>
            <div className="space-y-3 text-xs">
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 rounded-full bg-[#4E5D52] mt-1" />
                <div>
                  <div className="font-semibold text-[#222B25]">
                    v2.4 Final Draft
                  </div>
                  <div className="text-[11px] text-[#8B968D]">
                    Adyen failover script & DLQ procedures documented
                  </div>
                  <div className="text-[10px] text-[#8B968D]">Today, 2h ago</div>
                </div>
              </div>

              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 rounded-full bg-[#C9B79E] mt-1" />
                <div>
                  <div className="font-semibold text-[#222B25]">
                    v2.0 AI Synthesis
                  </div>
                  <div className="text-[11px] text-[#8B968D]">
                    Reconstructed from 47 Git and Slack sources
                  </div>
                  <div className="text-[10px] text-[#8B968D]">Yesterday</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {selectedConflict && (
        <ConflictResolutionModal
          conflict={selectedConflict}
          onClose={() => setSelectedConflict(null)}
          onResolved={fetchData}
        />
      )}

      {showPdf && handoverData && (
        <ExportPdfModal handoverData={handoverData} onClose={() => setShowPdf(false)} />
      )}
    </div>
  );
}
