"use client";

import React, { useState } from "react";
import { X, AlertTriangle, CheckCircle2, GitMerge } from "lucide-react";
import { api } from "@/lib/api";

interface ConflictResolutionProps {
  conflict: any | null;
  onClose: () => void;
  onResolved: () => void;
}

export function ConflictResolutionModal({
  conflict,
  onClose,
  onResolved,
}: ConflictResolutionProps) {
  const [resolutionNotes, setResolutionNotes] = useState(
    conflict?.recommended_fix || "Assign Payments Pod L2 triage; SRE retains automated restart without raw API tokens."
  );
  const [submitting, setSubmitting] = useState(false);

  if (!conflict) return null;

  const handleResolve = async () => {
    setSubmitting(true);
    try {
      await api.resolveConflict(conflict.id, {
        resolution_notes: resolutionNotes,
        accepted_fix: resolutionNotes,
      });
      onResolved();
      onClose();
    } catch (e) {
      console.error("Failed to resolve conflict:", e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs animate-in fade-in">
      <div className="w-full max-w-2xl bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#E5D5BF] flex items-center justify-between bg-[#FAF5EE]">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF]">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono font-semibold text-[#63513C]">
                {conflict.conflict_code} • UNRESOLVED AMBIGUITY
              </span>
              <h2 className="text-base font-bold text-[#222B25] leading-tight">
                {conflict.title}
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#8B968D] hover:text-[#222B25] hover:bg-[#EFE6D8]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-5 overflow-y-auto max-h-[70vh]">
          <p className="text-xs text-[#5E6F63] leading-relaxed">
            {conflict.description}
          </p>

          {/* Side by side conflicting sources */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Source A */}
            <div className="p-3.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] space-y-2">
              <div className="text-[11px] font-semibold text-[#8B968D] uppercase tracking-wider">
                Source A: {conflict.source_a_label || "Codebase PR #1420"}
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-[#E5D5BF] text-xs font-mono text-[#222B25] italic">
                {conflict.source_a_quote || '// circuit_breaker.go: line 104\ncircuit.Notify("pagerduty:core-sre");'}
              </div>
              <div className="text-xs font-medium text-[#63513C]">
                Claim: {conflict.source_a_claim || "Core Infra SRE owns manual overrides"}
              </div>
            </div>

            {/* Source B */}
            <div className="p-3.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] space-y-2">
              <div className="text-[11px] font-semibold text-[#8B968D] uppercase tracking-wider">
                Source B: {conflict.source_b_label || "Arch Sync Notes (Slack)"}
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-[#E5D5BF] text-xs font-mono text-[#222B25] italic">
                {conflict.source_b_quote || '"Sarah agreed Payments Pod owns manual drain triggers until Q1-25."'}
              </div>
              <div className="text-xs font-medium text-[#4E5D52]">
                Claim: {conflict.source_b_claim || "Payments Pod (Marcus) retains override triggers"}
              </div>
            </div>
          </div>

          {/* Recommended Resolution Box */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-[#222B25] flex items-center space-x-1.5">
              <GitMerge className="w-4 h-4 text-[#4E5D52]" />
              <span>Recommended Resolution / Human Sign-off Note:</span>
            </label>
            <textarea
              rows={3}
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              className="w-full p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25] focus:ring-2 focus:ring-[#4E5D52] focus:outline-hidden"
              placeholder="Enter authoritative reconciliation directive..."
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#E5D5BF] bg-[#FAF5EE] flex items-center justify-end space-x-2">
          <button
            onClick={onClose}
            className="py-2 px-4 rounded-xl border border-[#E5D5BF] bg-white text-xs font-medium text-[#4E5D52] hover:bg-[#F2EADB]"
          >
            Cancel
          </button>
          <button
            onClick={handleResolve}
            disabled={submitting}
            className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>{submitting ? "Resolving..." : "Accept Resolution & Update Ledger"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
