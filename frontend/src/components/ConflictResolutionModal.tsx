"use client";

import React, { useState } from "react";
import { X, AlertTriangle, CheckCircle2, GitMerge, HelpCircle, Ban } from "lucide-react";
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
    conflict?.recommended_fix || conflict?.resolution_notes || "Authoritative reconciliation confirmed."
  );
  const [submitting, setSubmitting] = useState(false);

  if (!conflict) return null;

  const handleResolveAction = async (status: "Resolved" | "Unresolved" | "Rejected") => {
    setSubmitting(true);
    try {
      await api.resolveConflict(conflict.id, {
        resolution_notes: resolutionNotes,
        accepted_fix: resolutionNotes,
        resolution_status: status,
      });
      onResolved();
      onClose();
    } catch (e: any) {
      alert(`Resolution error: ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const category = conflict.category || "Ownership";

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
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono font-semibold text-[#63513C]">
                  {conflict.conflict_code} • {conflict.resolution_status?.toUpperCase() || "PENDING"}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                  {category} Conflict
                </span>
              </div>
              <h2 className="text-base font-bold text-[#222B25] leading-tight mt-0.5">
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
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-[#8B968D] mb-1">
              Detection Explanation
            </div>
            <p className="text-xs text-[#5E6F63] leading-relaxed">
              {conflict.detection_reason || conflict.description}
            </p>
          </div>

          {/* Side by side conflicting sources */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Source A */}
            <div className="p-3.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] space-y-2">
              <div className="flex justify-between items-center text-[11px] font-semibold text-[#8B968D] uppercase tracking-wider">
                <span>Source A: {conflict.source_a_label || "Source Record A"}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-[#E5D5BF] text-xs font-mono text-[#222B25] italic leading-relaxed">
                "{conflict.source_a_quote || 'Verbatim quote from source A'}"
              </div>
              <div className="text-xs font-medium text-[#63513C]">
                Extracted Assertion: <strong className="font-semibold">{conflict.source_a_claim || conflict.source_a_value}</strong>
              </div>
            </div>

            {/* Source B */}
            <div className="p-3.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] space-y-2">
              <div className="flex justify-between items-center text-[11px] font-semibold text-[#8B968D] uppercase tracking-wider">
                <span>Source B: {conflict.source_b_label || "Source Record B"}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-[#E5D5BF] text-xs font-mono text-[#222B25] italic leading-relaxed">
                "{conflict.source_b_quote || 'Verbatim quote from source B'}"
              </div>
              <div className="text-xs font-medium text-[#4E5D52]">
                Extracted Assertion: <strong className="font-semibold">{conflict.source_b_claim || conflict.source_b_value}</strong>
              </div>
            </div>
          </div>

          {/* Recommended Resolution Box */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-[#222B25] flex items-center space-x-1.5">
              <GitMerge className="w-4 h-4 text-[#4E5D52]" />
              <span>Authoritative Reconciliation Directive / Clarification Notes:</span>
            </label>
            <textarea
              rows={3}
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              className="w-full p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25] focus:ring-2 focus:ring-[#4E5D52] focus:outline-hidden"
              placeholder="Enter authoritative reconciliation directive or clarification..."
            />
          </div>
        </div>

        {/* Footer with Accept, Reject, Mark Unresolved */}
        <div className="p-4 border-t border-[#E5D5BF] bg-[#FAF5EE] flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleResolveAction("Unresolved")}
              disabled={submitting}
              className="py-2 px-3 rounded-xl border border-[#C9B79E] bg-[#FAF5EE] text-xs font-medium text-[#63513C] hover:bg-[#F2EADB] flex items-center space-x-1"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Mark Unresolved</span>
            </button>
            <button
              onClick={() => handleResolveAction("Rejected")}
              disabled={submitting}
              className="py-2 px-3 rounded-xl border border-[#E5D5BF] bg-white text-xs font-medium text-rose-700 hover:bg-rose-50 flex items-center space-x-1"
            >
              <Ban className="w-3.5 h-3.5" />
              <span>Reject Discrepancy</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="py-2 px-3.5 rounded-xl border border-[#E5D5BF] bg-white text-xs font-medium text-[#4E5D52] hover:bg-[#F2EADB]"
            >
              Cancel
            </button>
            <button
              onClick={() => handleResolveAction("Resolved")}
              disabled={submitting}
              className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{submitting ? "Saving..." : "Accept Resolution & Update Ledger"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
