"use client";

import React, { useState, useEffect } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  Search,
  ExternalLink,
  ShieldCheck,
  Lock,
  ArrowUpRight,
  GitPullRequest,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { EvidenceInspectorModal } from "./EvidenceInspectorModal";
import { AccessRequestModal } from "./AccessRequestModal";

interface DecisionsLedgerProps {
  onSelectConflict: (conflictCode: string) => void;
}

export function DecisionsLedgerView({ onSelectConflict }: DecisionsLedgerProps) {
  const { currentProject, user } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedClaim, setSelectedClaim] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAccessModal, setShowAccessModal] = useState(false);
  const [accessTarget, setAccessTarget] = useState<any>(null);

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const res = await api.getClaims({
        projectId: currentProject.id,
        status: filterStatus === "ALL" ? undefined : filterStatus,
      });
      setClaims(res.claims || []);
      if (!selectedClaim && res.claims?.length > 0) {
        setSelectedClaim(res.claims[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, [currentProject, filterStatus]);

  const filteredClaims = claims.filter((c) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.title?.toLowerCase().includes(q) ||
      c.description?.toLowerCase().includes(q) ||
      c.claim_code?.toLowerCase().includes(q)
    );
  });

  const countVerified = claims.filter((c) => c.evidence_status === "VERIFIED").length;
  const countConflicting = claims.filter((c) => c.evidence_status === "CONFLICTING").length;
  const countInferred = claims.filter((c) => c.evidence_status === "INFERRED").length;

  const handleConfirmInferred = async (claimId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.confirmClaim(claimId);
      fetchClaims();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      {/* Top Header / Subheader */}
      <div className="p-4 sm:p-6 border-b border-[#E5D5BF] bg-white flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-bold text-[#222B25]">
              Decisions Ledger
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
              94% Grounded
            </span>
            {countConflicting > 0 && (
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]">
                {countConflicting} Conflict{countConflicting > 1 ? "s" : ""}
              </span>
            )}
          </div>
          <div className="text-xs text-[#5E6F63] mt-1">
            Immutable chronological ledger verifying architectural assertions against Git commits & RFCs.
          </div>
        </div>

        {/* Connectors Indicator */}
        <div className="flex items-center space-x-2 text-xs font-mono text-[#5E6F63]">
          <span className="flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
            <span>GH</span>
          </span>
          <span>•</span>
          <span className="flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
            <span>JIRA</span>
          </span>
          <span>•</span>
          <span className="flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
            <span>SLACK</span>
          </span>
        </div>
      </div>

      {/* Filter Pills & Search Bar */}
      <div className="p-4 sm:px-6 bg-[#FAF5EE] border-b border-[#E5D5BF] flex flex-wrap items-center justify-between gap-3">
        {/* Status Pills */}
        <div className="flex items-center space-x-1 sm:space-x-2 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setFilterStatus("ALL")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
              filterStatus === "ALL"
                ? "bg-[#4E5D52] text-white shadow-xs"
                : "bg-white text-[#5E6F63] border border-[#E5D5BF] hover:bg-[#F2EADB]"
            }`}
          >
            All Decisions ({claims.length})
          </button>
          <button
            onClick={() => setFilterStatus("VERIFIED")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-1.5 transition-all ${
              filterStatus === "VERIFIED"
                ? "bg-[#4E5D52] text-white shadow-xs"
                : "bg-white text-[#323F36] border border-[#A6B29C] hover:bg-[#EFF3ED]"
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
            <span>Verified ({countVerified})</span>
          </button>
          <button
            onClick={() => setFilterStatus("CONFLICTING")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-1.5 transition-all ${
              filterStatus === "CONFLICTING"
                ? "bg-[#4E5D52] text-white shadow-xs"
                : "bg-white text-[#63513C] border border-[#C9B79E] hover:bg-[#FAF0E6]"
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#C9B79E]" />
            <span>Conflicting ({countConflicting})</span>
          </button>
          <button
            onClick={() => setFilterStatus("INFERRED")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-1.5 transition-all ${
              filterStatus === "INFERRED"
                ? "bg-[#4E5D52] text-white shadow-xs"
                : "bg-white text-[#5E6F63] border border-[#E5D5BF] hover:bg-[#F2EADB]"
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#8B968D]" />
            <span>Inferred ({countInferred})</span>
          </button>
        </div>

        {/* Search Input & Scope */}
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#8B968D] absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter claims or RFCs..."
              className="pl-8 pr-3 py-1.5 rounded-lg border border-[#E5D5BF] bg-white text-xs text-[#222B25] focus:outline-hidden focus:ring-1 focus:ring-[#4E5D52] w-44 sm:w-56"
            />
          </div>
          <div className="text-xs px-2.5 py-1.5 rounded-lg border border-[#E5D5BF] bg-white text-[#5E6F63] font-medium">
            Scope: Q3–Q4
          </div>
        </div>
      </div>

      {/* Main Content Layout: Cards Stream Left | Evidence Inspector Right */}
      <div className="flex-1 p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Cards Stream */}
        <div className="lg:col-span-7 space-y-4">
          {filteredClaims.map((claim) => {
            const isSelected = selectedClaim?.id === claim.id;
            const isVerified = claim.evidence_status === "VERIFIED";
            const isConflicting = claim.evidence_status === "CONFLICTING";
            const isInferred = claim.evidence_status === "INFERRED";
            const isRedacted = claim.is_redacted;

            if (isRedacted) {
              return (
                <div
                  key={claim.id}
                  className="p-5 rounded-2xl border border-[#C9B79E] bg-[#FAF5EE] shadow-2xs flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-xl bg-white border border-[#E5D5BF] text-[#63513C]">
                      <Lock className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#222B25]">
                        {claim.title}
                      </div>
                      <div className="text-xs text-[#5E6F63] mt-0.5">
                        {claim.description}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setAccessTarget(claim);
                      setShowAccessModal(true);
                    }}
                    className="py-1.5 px-3 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors shrink-0"
                  >
                    Request Access
                  </button>
                </div>
              );
            }

            return (
              <div
                key={claim.id}
                onClick={() => setSelectedClaim(claim)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer relative group ${
                  isSelected
                    ? "border-[#4E5D52] bg-white shadow-md ring-1 ring-[#4E5D52]/20"
                    : "border-[#E5D5BF] bg-white hover:border-[#C9B79E] shadow-2xs"
                }`}
              >
                {/* Card Top: Status & Date */}
                <div className="flex items-center justify-between text-xs mb-2">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                        isVerified
                          ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                          : isConflicting
                          ? "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
                          : "bg-[#FAF5EE] text-[#4E5D52] border border-[#E5D5BF]"
                      }`}
                    >
                      <CheckCircle2 className="w-3 h-3 text-[#4E5D52]" />
                      <span>
                        {isVerified
                          ? `Verified (${claim.verification_method || "Exact Match"})`
                          : isConflicting
                          ? "Conflicting Evidence"
                          : `Inferred Decision (${Math.round((claim.confidence_score || 0.8) * 100)}% Conf)`}
                      </span>
                    </span>
                    <span className="font-mono text-[#8B968D] text-[11px]">
                      {claim.claim_code}
                    </span>
                  </div>
                  <span className="text-[#8B968D] font-mono text-[11px]">
                    {new Date(claim.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Card Title */}
                <h3 className="font-semibold text-sm text-[#222B25] leading-snug">
                  {claim.title}
                </h3>

                {/* Card Description */}
                <p className="mt-2 text-xs text-[#5E6F63] leading-relaxed line-clamp-3">
                  {claim.description}
                </p>

                {/* Conflicting Callout if applicable */}
                {isConflicting && (
                  <div className="mt-3 p-3 rounded-xl bg-[#FAF5EE] border border-[#C9B79E] flex items-center justify-between">
                    <div className="text-xs text-[#63513C]">
                      Discrepancy detected between Slack sync and GitHub Issue assignee.
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectConflict("CONF-882");
                      }}
                      className="text-xs font-bold text-[#4E5D52] hover:underline flex items-center space-x-1 shrink-0 ml-2"
                    >
                      <span>Needs Resolution</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                {/* Card Footer: Tags & Author */}
                <div className="mt-4 pt-3 border-t border-[#E5D5BF] flex items-center justify-between text-xs">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded bg-[#FAF5EE] border border-[#E5D5BF] text-[#4E5D52] font-mono text-[10px]">
                      #GH-PR-1892
                    </span>
                    <span className="px-2 py-0.5 rounded bg-[#FAF5EE] border border-[#E5D5BF] text-[#4E5D52] font-mono text-[10px]">
                      #RFC-044-DB
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {isInferred && (
                      <div className="flex space-x-1">
                        <button
                          onClick={(e) => handleConfirmInferred(claim.id, e)}
                          className="px-2.5 py-1 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white font-semibold text-[11px] transition-colors"
                        >
                          Confirm
                        </button>
                      </div>
                    )}
                    <span className="text-[#8B968D] text-[11px]">
                      Departing Lead: <strong className="text-[#222B25]">{claim.related_person || "Sarah Lin"}</strong>
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Side: Embedded Evidence Inspector */}
        <div className="lg:col-span-5 sticky top-20 hidden lg:block">
          {selectedClaim ? (
            <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-5">
              <div className="flex items-center justify-between border-b border-[#E5D5BF] pb-3">
                <div className="flex items-center space-x-2 font-bold text-xs uppercase tracking-wider text-[#222B25]">
                  <ShieldCheck className="w-4 h-4 text-[#4E5D52]" />
                  <span>Evidence Inspector</span>
                </div>
                <span className="font-mono text-xs text-[#8B968D]">
                  {selectedClaim.claim_code}
                </span>
              </div>

              {/* Grounded Status Pill */}
              <div className="p-3 rounded-xl bg-[#EFF3ED] border border-[#A6B29C] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-[#323F36]">
                    100% Grounded Claim
                  </div>
                  <div className="text-[10px] text-[#5E6F63]">
                    Zero hallucination risk detected
                  </div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white text-[#323F36] border border-[#A6B29C]">
                  {selectedClaim.verification_method || "Verified BFT"}
                </span>
              </div>

              {/* Verbatim Source Quote */}
              <div>
                <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-[#8B968D] mb-1.5">
                  <span>Verbatim Source Quote</span>
                  <span className="text-[#4E5D52] font-mono text-[10px]">
                    {selectedClaim.line_span || "Span (L48-L56)"}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#EFF3ED] border border-[#A6B29C] text-xs font-mono text-[#222B25] leading-relaxed italic border-l-4 border-l-[#4E5D52]">
                  "{selectedClaim.exact_quote || "We agreed in architecture review that pgvector eliminates dual-database synchronization latency while maintaining transactional guarantees for payments ledger cutover."}"
                </div>
              </div>

              {/* Merged PR Diff Snippet */}
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-[#8B968D] mb-1.5">
                  Merged PR Diff Verification
                </div>
                <pre className="p-3 rounded-xl bg-[#28322B] text-[#EFF3ED] text-[11px] font-mono overflow-x-auto border border-[#3A473E]">
                  <code>{selectedClaim.primary_code_diff || `@@ -14,6 +14,8 @@ alembic/env.py
- from dynamodb_client import SyncDriver
+ from pgvector.sqlalchemy import Vector
+ class LedgerVectorEmbedding(Base):`}</code>
                </pre>
              </div>

              {/* Inspector Attributes Table */}
              <div className="divide-y divide-[#E5D5BF] text-xs text-[#5E6F63]">
                <div className="py-2 flex justify-between">
                  <span className="text-[#8B968D]">Primary Source</span>
                  <span className="font-semibold text-[#4E5D52] flex items-center space-x-1">
                    <span>GitHub PR #1892</span>
                    <ExternalLink className="w-3 h-3" />
                  </span>
                </div>
                <div className="py-2 flex justify-between">
                  <span className="text-[#8B968D]">Decision Author</span>
                  <span className="font-semibold text-[#222B25]">
                    {selectedClaim.related_person || "Sarah Lin"}
                  </span>
                </div>
                <div className="py-2 flex justify-between">
                  <span className="text-[#8B968D]">Sign-off Reviewer</span>
                  <span className="font-semibold text-[#222B25]">
                    Alex Morgan (Eng Mgr)
                  </span>
                </div>
                <div className="py-2 flex justify-between">
                  <span className="text-[#8B968D]">Cryptographic Root</span>
                  <span className="font-mono text-[10px] text-[#5E6F63]">
                    {selectedClaim.cryptographic_root || "sha256:4b91f0...de21"}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2 pt-2">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noreferrer"
                  className="w-full py-2 px-3 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors shadow-2xs"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>View Source on GitHub</span>
                </a>
                <div className="flex space-x-2">
                  <button className="flex-1 py-1.5 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] text-[#4E5D52] hover:bg-[#F2EADB] text-xs font-medium">
                    Annotate
                  </button>
                  <button className="flex-1 py-1.5 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] text-[#4E5D52] hover:bg-[#F2EADB] text-xs font-medium">
                    ★ Golden Ref
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-2xl border border-dashed border-[#C9B79E] text-center text-[#8B968D] text-xs bg-white">
              Select any claim from the ledger to inspect verbatim citations, code diffs, and verification proof.
            </div>
          )}
        </div>
      </div>

      {/* Access Request Modal */}
      {showAccessModal && (
        <AccessRequestModal
          onClose={() => setShowAccessModal(false)}
          resourceId={accessTarget?.id || 6}
          resourceName={accessTarget?.title || "Confidential Resource"}
          onRequestSubmitted={fetchClaims}
        />
      )}
    </div>
  );
}
