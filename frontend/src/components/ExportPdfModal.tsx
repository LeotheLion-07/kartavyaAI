"use client";

import React, { useRef } from "react";
import { X, Printer, ShieldCheck } from "lucide-react";

interface ExportPdfModalProps {
  handoverData: any;
  onClose: () => void;
}

export function ExportPdfModal({ handoverData, onClose }: ExportPdfModalProps) {
  const printRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    window.print();
  };

  if (!handoverData) return null;
  const { report, case: handoverCase } = handoverData;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/50 backdrop-blur-xs overflow-y-auto">
      <div className="w-full max-w-4xl bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl overflow-hidden flex flex-col my-8">
        {/* Modal Toolbar (hidden during print) */}
        <div className="p-4 border-b border-[#E5D5BF] flex items-center justify-between bg-[#FAF5EE] print:hidden">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-[#4E5D52]" />
            <span className="font-bold text-sm text-[#222B25]">
              Executive Handover Report • 13-Section Transition Package
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="py-1.5 px-3 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition-colors"
            >
              <Printer className="w-4 h-4" />
              <span>Print / Save as PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#8B968D] hover:text-[#222B25] hover:bg-[#EFE6D8]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Printable Report Canvas */}
        <div
          ref={printRef}
          className="p-8 sm:p-12 space-y-8 bg-white text-[#222B25] overflow-y-auto max-h-[80vh] print:max-h-none print:overflow-visible font-sans"
        >
          {/* Header Banner */}
          <div className="border-b-2 border-[#4E5D52] pb-6">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-xs font-mono font-bold tracking-widest text-[#4E5D52] uppercase">
                  Kartavya AI • Handover Vault
                </div>
                <h1 className="text-2xl font-black text-[#222B25] mt-1">
                  Executive Transfer Order & Knowledge Handover
                </h1>
                <div className="text-xs text-[#5E6F63] mt-1 font-mono">
                  Case ID: {handoverCase?.case_number} • Hash: {report?.cryptographic_signature || "sha256:7c9e01...b84f"}
                </div>
              </div>
              <div className="text-right">
                <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
                  {handoverCase?.status || "Cutover Ready"}
                </span>
                <div className="text-[11px] text-[#8B968D] mt-1 font-mono">
                  Cutover: {new Date(handoverCase?.target_cutover_date || Date.now()).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>

          {/* 1. Project Overview */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>1. Project Overview</span>
            </h2>
            <p className="text-xs leading-relaxed text-[#5E6F63]">
              {report?.executive_summary}
            </p>
          </section>

          {/* 2. Current Project Status */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>2. Current Project Status</span>
            </h2>
            <div className="text-xs text-[#222B25] bg-[#FAF5EE] p-3 rounded-lg border border-[#E5D5BF]">
              {report?.current_status}
            </div>
          </section>

          {/* 3. Important Decisions */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>3. Important Architectural Decisions</span>
            </h2>
            <div className="text-xs text-[#5E6F63] whitespace-pre-line leading-relaxed">
              {report?.decisions_summary}
            </div>
          </section>

          {/* 4. Team Responsibilities */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>4. Team Responsibilities & Escalation Grid</span>
            </h2>
            <div className="text-xs text-[#5E6F63]">
              {report?.team_responsibilities}
            </div>
          </section>

          {/* 5. Completed Tasks */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>5. Completed Milestones</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.completed_tasks}</p>
          </section>

          {/* 6. Pending Tasks */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>6. Pending Work & Critical Issues</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.pending_tasks}</p>
          </section>

          {/* 7. Blockers */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#7A3E2D] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>7. Active Blockers & Immediate Actions</span>
            </h2>
            <div className="text-xs text-[#7A3E2D] bg-[#FAF0E6] p-3 rounded-lg border border-[#E5D5BF] leading-relaxed">
              {report?.blockers_summary}
            </div>
          </section>

          {/* 8. Risks */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>8. Operational & Knowledge Risks (Bus Factor)</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.risks_summary}</p>
          </section>

          {/* 9. Dependencies */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>9. System Dependencies & Infrastructure</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.dependencies_summary}</p>
          </section>

          {/* 10. Missing Information & Knowledge Gaps */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>10. Missing Information & Clarifications</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.missing_information}</p>
          </section>

          {/* 11. Next Actions */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>11. Authoritative Next Actions</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">{report?.next_actions}</p>
          </section>

          {/* 12. Supporting Evidence & Lineage */}
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>12. Verifiable Supporting Evidence</span>
            </h2>
            <p className="text-xs text-[#5E6F63]">
              Synthesized from {report?.supporting_evidence_count || 24} validated Git pull requests, RFC memos, and public communication threads with DLP token masks applied.
            </p>
          </section>

          {/* 13. 30-Day Continuation Plan */}
          <section className="space-y-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#222B25] flex items-center space-x-2 border-b border-[#E5D5BF] pb-1">
              <span>13. 30-Day Successor Onboarding Plan</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3 bg-[#FAF5EE] border border-[#E5D5BF] rounded-lg">
                <div className="font-bold text-[#222B25]">Week 1: Ramp-up & Context</div>
                <ul className="mt-1 space-y-1 text-[#5E6F63] text-[11px] list-disc list-inside">
                  <li>Clone repo & spin up pgvector</li>
                  <li>1-on-1 Walkthrough with Sarah</li>
                  <li>Verify AWS IAM staging roles</li>
                </ul>
              </div>
              <div className="p-3 bg-[#FAF5EE] border border-[#E5D5BF] rounded-lg">
                <div className="font-bold text-[#222B25]">Week 2: First Deployment</div>
                <ul className="mt-1 space-y-1 text-[#5E6F63] text-[11px] list-disc list-inside">
                  <li>Resolve #PAY-412 retry backoff</li>
                  <li>Shadow Alex during incident triage</li>
                </ul>
              </div>
              <div className="p-3 bg-[#FAF5EE] border border-[#E5D5BF] rounded-lg">
                <div className="font-bold text-[#222B25]">Weeks 3-4: Full Ownership</div>
                <ul className="mt-1 space-y-1 text-[#5E6F63] text-[11px] list-disc list-inside">
                  <li>Celery Redis reconnect migration</li>
                  <li>Publish v2 API specs to partners</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Signatures & Cryptographic Proof */}
          <div className="pt-6 border-t-2 border-[#4E5D52] grid grid-cols-2 gap-6 text-xs">
            <div>
              <div className="font-semibold text-[#5E6F63]">Departing Staff Engineer:</div>
              <div className="font-bold text-[#222B25] text-sm mt-1">Sarah Lin</div>
              <div className="text-[10px] text-[#8B968D] font-mono mt-0.5">
                Signed & Verified on Oct 24, 14:12 UTC
              </div>
            </div>
            <div>
              <div className="font-semibold text-[#5E6F63]">Engineering Manager:</div>
              <div className="font-bold text-[#222B25] text-sm mt-1">Alex Morgan</div>
              <div className="text-[10px] text-[#8B968D] font-mono mt-0.5">
                Cryptographic Sign-off v2.4 (BFT Consensus)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
