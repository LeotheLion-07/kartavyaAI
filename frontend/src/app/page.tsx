"use client";

import React, { useState } from "react";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { RoleHandoverView } from "@/components/RoleHandoverView";
import { DecisionsLedgerView } from "@/components/DecisionsLedgerView";
import { EvidenceBoardView } from "@/components/EvidenceBoardView";
import { SourcesIngestionView } from "@/components/SourcesIngestionView";
import { KnowledgeGapsView } from "@/components/KnowledgeGapsView";
import { GroundedChatView } from "@/components/GroundedChatView";
import { AuditLogsView } from "@/components/AuditLogsView";
import { EvidenceInspectorModal } from "@/components/EvidenceInspectorModal";
import { ConflictResolutionModal } from "@/components/ConflictResolutionModal";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("role-handover");
  const [inspectedClaim, setInspectedClaim] = useState<any | null>(null);
  const [activeConflict, setActiveConflict] = useState<any | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F0E6] text-[#222B25] font-sans selection:bg-[#4E5D52] selection:text-white">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        gapsCount={3}
      />

      {/* Main Container: Sidebar + Tab Content */}
      <div className="flex-1 flex min-w-0">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          gapsCount={3}
        />

        <main className="flex-1 flex flex-col min-w-0 bg-[#F6F0E6] overflow-hidden">
          {activeTab === "role-handover" && (
            <RoleHandoverView
              onOpenInspector={(claim) => setInspectedClaim(claim)}
              onOpenChat={() => setActiveTab("chat")}
            />
          )}

          {activeTab === "timeline" && (
            <DecisionsLedgerView
              onSelectConflict={() => {
                setActiveConflict({
                  id: 1,
                  conflict_code: "CONF-882",
                  title: "Webhook Failover Circuit Breaker Ownership Discrepancy",
                  description:
                    "Two canonical systems assign differing primary on-call tiers for the Stripe & Adyen webhook reconciliation pipeline.",
                  source_a_label: "Codebase PR #1420 (Sep 12)",
                  source_a_quote:
                    '// circuit_breaker.go: line 104\ncircuit.Notify("pagerduty:core-sre");',
                  source_a_claim: "Core Infra SRE owns manual overrides",
                  source_b_label: "Arch Sync Notes (Slack) (Oct 04)",
                  source_b_quote:
                    '"Sarah agreed Payments Pod owns manual drain triggers until Q1-25. SRE only receives metric pings."',
                  source_b_claim: "Payments Pod (Marcus) retains override triggers",
                  recommended_fix:
                    "Assign Payments Pod L2 triage; SRE retains automated restart without raw API tokens.",
                });
              }}
            />
          )}

          {activeTab === "evidence" && (
            <EvidenceBoardView
              onOpenConflictModal={() => {
                setActiveConflict({
                  id: 1,
                  conflict_code: "CONF-882",
                  title: "Webhook Failover Circuit Breaker Ownership Discrepancy",
                  description:
                    "Two canonical systems assign differing primary on-call tiers for the Stripe & Adyen webhook reconciliation pipeline.",
                  source_a_label: "Codebase PR #1420 (Sep 12)",
                  source_a_quote:
                    '// circuit_breaker.go: line 104\ncircuit.Notify("pagerduty:core-sre");',
                  source_a_claim: "Core Infra SRE owns manual overrides",
                  source_b_label: "Arch Sync Notes (Slack) (Oct 04)",
                  source_b_quote:
                    '"Sarah agreed Payments Pod owns manual drain triggers until Q1-25. SRE only receives metric pings."',
                  source_b_claim: "Payments Pod (Marcus) retains override triggers",
                  recommended_fix:
                    "Assign Payments Pod L2 triage; SRE retains automated restart without raw API tokens.",
                });
              }}
            />
          )}

          {activeTab === "sources" && <SourcesIngestionView />}

          {activeTab === "gaps" && <KnowledgeGapsView />}

          {activeTab === "chat" && <GroundedChatView />}

          {activeTab === "audit" && <AuditLogsView />}
        </main>
      </div>

      {/* Global Modals */}
      {inspectedClaim && (
        <EvidenceInspectorModal
          claim={inspectedClaim}
          onClose={() => setInspectedClaim(null)}
        />
      )}

      {activeConflict && (
        <ConflictResolutionModal
          conflict={activeConflict}
          onClose={() => setActiveConflict(null)}
          onResolved={() => {
            setActiveConflict(null);
            alert("Conflict resolved and synced across ledger.");
          }}
        />
      )}
    </div>
  );
}
