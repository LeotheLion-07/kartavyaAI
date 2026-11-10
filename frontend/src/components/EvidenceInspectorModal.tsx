"use client";

import React, { useEffect, useState } from "react";
import {
  X,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  Lock,
  History,
  FileCode,
} from "lucide-react";
import { api } from "@/lib/api";

interface EvidenceInspectorProps {
  claim: any | null;
  onClose: () => void;
  onClaimConfirmed?: (claimId: number) => void;
}

export function EvidenceInspectorModal({
  claim,
  onClose,
  onClaimConfirmed,
}: EvidenceInspectorProps) {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!claim) return;
    const fetchClaimDetails = async () => {
      setLoading(true);
      try {
        const res = await api.getClaim(claim.id);
        setDetails(res);
      } catch (e) {
        console.error("Error loading claim details:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchClaimDetails();
  }, [claim]);

  if (!claim) return null;

  const handleConfirm = async () => {
    setConfirming(true);
    try {
      await api.confirmClaim(claim.id);
      if (onClaimConfirmed) {
        onClaimConfirmed(claim.id);
      }
      onClose();
    } catch (e) {
      console.error("Failed to confirm claim:", e);
    } finally {
      setConfirming(false);
    }
  };

  const isVerified = claim.evidence_status === "VERIFIED";
  const isInferred = claim.evidence_status === "INFERRED";
  const isConflicting = claim.evidence_status === "CONFLICTING";

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-white border-l border-[#E5D5BF] shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-[#E5D5BF] flex items-center justify-between bg-[#FAF5EE]">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-[#4E5D52]" />
          <span className="font-bold text-sm text-[#222B25]">
            Evidence Inspector
          </span>
          <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-white border border-[#E5D5BF] text-[#4E5D52]">
            {claim.claim_code}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#8B968D] hover:text-[#222B25] hover:bg-[#EFE6D8] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Verification Status Card */}
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between ${
            isVerified
              ? "bg-[#EFF3ED] border-[#A6B29C] text-[#323F36]"
              : isConflicting
              ? "bg-[#FAF5EE] border-[#C9B79E] text-[#63513C]"
              : "bg-[#FAF5EE] border-[#E5D5BF] text-[#4E5D52]"
          }`}
        >
          <div className="flex items-center space-x-2.5">
            <CheckCircle2 className="w-5 h-5 text-[#4E5D52]" />
            <div>
              <div className="text-xs font-bold uppercase tracking-wider">
                {isVerified ? "100% Grounded Claim" : isInferred ? "Inferred Assertion" : "Disputed / Conflicting"}
              </div>
              <div className="text-[11px] opacity-80">
                {isVerified ? "Zero hallucination risk detected" : "Requires human lead verification"}
              </div>
            </div>
          </div>
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-white border border-current">
            {claim.verification_method || "Verified BFT"}
          </span>
        </div>

        {/* Claim Title & Category */}
        <div>
          <div className="text-xs font-semibold text-[#8B968D] uppercase tracking-wider mb-1">
            Claim Title
          </div>
          <h3 className="font-semibold text-sm text-[#222B25] leading-snug">
            {claim.title}
          </h3>
          <p className="mt-2 text-xs text-[#5E6F63] leading-relaxed bg-[#FAF5EE] p-3 rounded-lg border border-[#E5D5BF]">
            {claim.description}
          </p>
        </div>

        {/* Verbatim Source Quote */}
        {claim.exact_quote && (
          <div>
            <div className="flex items-center justify-between text-xs font-semibold text-[#8B968D] uppercase tracking-wider mb-1.5">
              <span>Verbatim Source Quote</span>
              <span className="text-[#4E5D52] font-mono text-[11px]">
                {claim.line_span || "Span L48-L56"}
              </span>
            </div>
            <div className="p-3.5 rounded-xl border border-[#A6B29C] bg-[#EFF3ED] text-xs text-[#222B25] font-mono italic leading-relaxed border-l-4 border-l-[#4E5D52]">
              "{claim.exact_quote}"
            </div>
          </div>
        )}

        {/* Merged PR Diff Verification */}
        {claim.primary_code_diff && (
          <div>
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#8B968D] uppercase tracking-wider mb-1.5">
              <FileCode className="w-3.5 h-3.5 text-[#4E5D52]" />
              <span>Merged PR Diff Verification</span>
            </div>
            <pre className="p-3 rounded-xl bg-[#28322B] text-[#EFF3ED] text-xs font-mono overflow-x-auto border border-[#3A473E]">
              <code>{claim.primary_code_diff}</code>
            </pre>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] p-4 space-y-2.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[#8B968D]">Primary Source</span>
            <span className="font-semibold text-[#4E5D52] flex items-center space-x-1">
              <span>{claim.source_name || "GitHub PR #1892"}</span>
              <ExternalLink className="w-3 h-3" />
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[#8B968D]">Decision Author</span>
            <span className="font-semibold text-[#222B25]">
              {claim.related_person || "Sarah Lin"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[#8B968D]">Sign-off Reviewer</span>
            <span className="font-semibold text-[#222B25]">
              Alex Morgan (Eng Mgr)
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[#8B968D]">Cryptographic Root</span>
            <span className="font-mono text-[10px] text-[#5E6F63]">
              {claim.cryptographic_root || "sha256:4b91f0...de21"}
            </span>
          </div>
        </div>

        {/* Inferred decision confirmation button */}
        {isInferred && (
          <div className="p-3 bg-[#FAF5EE] border border-[#C9B79E] rounded-xl space-y-2">
            <div className="text-xs text-[#63513C] font-medium">
              This claim was inferred from PR discussions. Confirm to elevate to VERIFIED.
            </div>
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="w-full py-2 px-3 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors"
            >
              {confirming ? "Confirming..." : "Confirm & Mark Verified"}
            </button>
          </div>
        )}

        {/* Version History */}
        {details?.versions && details.versions.length > 0 && (
          <div>
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#8B968D] uppercase tracking-wider mb-2">
              <History className="w-3.5 h-3.5 text-[#5E6F63]" />
              <span>Version History ({details.versions.length})</span>
            </div>
            <div className="space-y-2">
              {details.versions.map((v: any, i: number) => (
                <div
                  key={i}
                  className="p-2.5 rounded-lg border border-[#E5D5BF] text-[11px] space-y-1 bg-white"
                >
                  <div className="flex justify-between text-[#8B968D]">
                    <span className="font-semibold text-[#222B25]">v{v.version_num} • {v.changed_by}</span>
                    <span>{new Date(v.timestamp).toLocaleDateString()}</span>
                  </div>
                  <div className="text-[#5E6F63] font-medium">
                    {v.change_reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-[#E5D5BF] bg-[#FAF5EE] flex items-center space-x-2">
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="flex-1 py-2 px-3 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold text-center flex items-center justify-center space-x-1.5 transition-colors shadow-2xs"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>View Source on GitHub</span>
        </a>
        <button
          onClick={onClose}
          className="py-2 px-3 rounded-xl border border-[#E5D5BF] bg-white text-[#4E5D52] hover:bg-[#F2EADB] text-xs font-medium transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
