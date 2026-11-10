"use client";

import React from "react";
import {
  GitCommit,
  ShieldCheck,
  UserCheck,
  Database,
  HelpCircle,
  MessageSquare,
  History,
  Lock,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  gapsCount?: number;
}

export function Sidebar({ activeTab, setActiveTab, gapsCount = 3 }: SidebarProps) {
  const navLinks = [
    { id: "timeline", label: "Decision Timeline", icon: GitCommit },
    { id: "evidence", label: "Evidence & Review", icon: ShieldCheck },
    { id: "role-handover", label: "Role Handover", icon: UserCheck },
    { id: "sources", label: "Sources & Ingestion", icon: Database },
    { id: "gaps", label: "Knowledge Gaps", icon: HelpCircle, badge: gapsCount },
    { id: "chat", label: "Grounded Q&A", icon: MessageSquare },
    { id: "audit", label: "Audit Logs", icon: History },
  ];

  return (
    <aside className="w-64 border-r border-[#E5D5BF] bg-[#FAF5EE] p-4 flex flex-col justify-between hidden md:flex shrink-0 min-h-[calc(100vh-3.75rem)]">
      <div className="space-y-6">
        <div>
          <div className="flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold text-[#8B968D] uppercase tracking-wider">
            <span>Navigation</span>
          </div>
          <div className="mt-2 space-y-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? "bg-[#4E5D52] text-white font-semibold shadow-xs"
                      : "text-[#5E6F63] hover:text-[#222B25] hover:bg-[#EFE6D8]"
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-[#8B968D]"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full ${
                        isActive
                          ? "bg-white/25 text-white"
                          : "bg-[#EFF3ED] text-[#4E5D52] border border-[#A6B29C]"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Audit Mode Status */}
        <div className="rounded-xl border border-[#E5D5BF] bg-white p-3 shadow-2xs">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#A6B29C] animate-pulse" />
            <span className="text-xs font-semibold text-[#222B25]">
              Audit Mode Active
            </span>
          </div>
          <div className="mt-1 text-[11px] font-mono text-[#5E6F63] truncate">
            Digest: 0x9f83...9e32
          </div>
          <div className="mt-2 text-[10px] text-[#8B968D] flex items-center space-x-1">
            <Lock className="w-3 h-3 text-[#A6B29C]" />
            <span>Immutable Git Ledger</span>
          </div>
        </div>
      </div>

      {/* Current Cutover Order Footer */}
      <div className="pt-4 border-t border-[#E5D5BF]">
        <div className="flex items-center space-x-2 px-2.5 py-2 rounded-lg bg-white border border-[#E5D5BF] text-xs">
          <div className="w-6 h-6 rounded-full bg-[#4E5D52] text-white flex items-center justify-center font-bold text-[10px]">
            SL
          </div>
          <div className="flex-1 truncate">
            <div className="font-semibold text-[#222B25] text-[11px] truncate">
              Sarah Lin → Marcus
            </div>
            <div className="text-[10px] text-[#8B968D] truncate">Core Platform & Payments</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
