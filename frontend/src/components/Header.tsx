"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import {
  ShieldCheck,
  CheckCircle2,
  ChevronDown,
  Layers,
  Menu,
  X,
  GitCommit,
  UserCheck,
  Database,
  HelpCircle,
  MessageSquare,
  History,
} from "lucide-react";

interface HeaderProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
  gapsCount?: number;
}

export function Header({ activeTab, setActiveTab, gapsCount = 3 }: HeaderProps) {
  const { user, sampleUsers, switchUser, currentProject, setCurrentProject } = useAuth();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabTitles: Record<string, string> = {
    "role-handover": "Role Handover",
    "timeline": "Decisions Ledger",
    "evidence": "Evidence & Review",
    "sources": "Sources & Ingestion",
    "gaps": "Knowledge Gaps",
    "chat": "Grounded Q&A",
    "audit": "Audit Logs",
  };

  const projects = [
    {
      id: 1,
      name: "Core Platform & Payments",
      slug: "core-platform-payments",
      description: "High-throughput payment settlement engine (4,500 req/s), pgvector HNSW ledger",
    },
    {
      id: 2,
      name: "AI-Powered Campus Management",
      slug: "campus-management-system",
      description: "University biometric auth, cafeteria POS ledger dual-write, course RAG",
    },
  ];

  const mobileNavLinks = [
    { id: "timeline", label: "Decision Timeline", icon: GitCommit },
    { id: "evidence", label: "Evidence Board", icon: ShieldCheck },
    { id: "role-handover", label: "Role Handover", icon: UserCheck },
    { id: "sources", label: "Sources & Ingestion", icon: Database },
    { id: "gaps", label: "Knowledge Gaps", icon: HelpCircle, badge: gapsCount },
    { id: "chat", label: "Grounded Q&A", icon: MessageSquare },
    { id: "audit", label: "Audit Logs", icon: History },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#E5D5BF] bg-white/95 backdrop-blur transition-colors">
      <div className="flex h-15 items-center justify-between px-4 sm:px-6">
        {/* Left: Brand Breadcrumb & Badges - Zero menu options in top bar */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2.5">
            <span className="font-bold text-lg tracking-tight text-[#222B25]">
              Kartavya AI
            </span>
            <span className="text-[#C9B79E] font-light">/</span>
            <span className="text-sm font-semibold text-[#4E5D52]">
              {tabTitles[activeTab || "role-handover"] || "Role Handover"}
            </span>
          </div>

          {/* Verification & Conflict Badges */}
          <div className="hidden sm:flex items-center space-x-2 ml-1">
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
              <span>94% Grounded</span>
            </span>

            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#C9B79E]" />
              <span>1 Conflict</span>
            </span>
          </div>

          <div className="hidden xl:block h-4 w-[1px] bg-[#E5D5BF] mx-1" />

          {/* Project / Scope Switcher */}
          <div className="relative hidden md:block">
            <button
              onClick={() => setProjectDropdownOpen(!projectDropdownOpen)}
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] hover:bg-[#F2EADB] text-xs font-medium text-[#4E5D52] transition-colors"
            >
              <Layers className="w-3.5 h-3.5 text-[#4E5D52]" />
              <span className="truncate max-w-[150px] font-semibold">{currentProject.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-[#C9B79E]" />
            </button>

            {projectDropdownOpen && (
              <div className="absolute left-0 mt-2 w-72 rounded-xl bg-white border border-[#E5D5BF] shadow-xl py-2 z-50">
                <div className="px-3 py-1 text-[11px] font-semibold text-[#8B968D] uppercase tracking-wider">
                  Select Scope / Project
                </div>
                {projects.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setCurrentProject(p);
                      setProjectDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs hover:bg-[#FAF5EE] flex flex-col transition-colors ${
                      currentProject.id === p.id
                        ? "bg-[#FAF5EE] text-[#4E5D52] font-semibold border-l-3 border-[#4E5D52]"
                        : "text-[#4E5D52]"
                    }`}
                  >
                    <span>{p.name}</span>
                    <span className="text-[10px] text-[#8B968D] truncate">{p.description}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Source Badges, Consensus Pill, Role Switcher & Mobile Menu Toggle */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Integrated Source Badges from Image 2 */}
          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#FAF5EE] text-[#5E6F63] border border-[#E5D5BF]">
            <span className="flex items-center space-x-1 text-[#323F36]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
              <span className="font-semibold">GH</span>
            </span>
            <span className="text-[#C9B79E]">•</span>
            <span className="flex items-center space-x-1 text-[#323F36]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
              <span className="font-semibold">JIRA</span>
            </span>
            <span className="text-[#C9B79E]">•</span>
            <span className="flex items-center space-x-1 text-[#323F36]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
              <span className="font-semibold">SLACK</span>
            </span>
          </div>

          {/* BFT Consensus status pill in Sage Green */}
          <div className="hidden sm:inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C] animate-pulse" />
            <span>BFT Consensus Verified (3/3)</span>
          </div>

          {/* User & Role Switcher */}
          <div className="relative">
            <button
              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              className="flex items-center space-x-2 p-1 pl-2 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] hover:bg-[#F2EADB] transition-colors"
            >
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.full_name}
                  className="w-7 h-7 rounded-full object-cover ring-1 ring-[#A6B29C]"
                />
              ) : (
                <div className="w-7 h-7 rounded-full bg-[#4E5D52] text-white text-xs flex items-center justify-center font-bold">
                  {user?.full_name?.charAt(0) || "U"}
                </div>
              )}
              <div className="hidden md:flex flex-col text-left text-xs leading-tight">
                <span className="font-semibold text-[#222B25]">
                  {user?.full_name || "Alex Morgan"}
                </span>
                <span className="text-[10px] text-[#5E6F63]">
                  {user?.title || "Eng Manager"}
                </span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-[#C9B79E]" />
            </button>

            {userDropdownOpen && (
              <div className="absolute right-0 mt-2 w-72 rounded-xl bg-white border border-[#E5D5BF] shadow-2xl py-2 z-50">
                <div className="px-3 py-1.5 border-b border-[#E5D5BF] mb-1">
                  <div className="text-[11px] font-semibold text-[#4E5D52] uppercase tracking-wider">
                    Simulate Role (1-Click Switch)
                  </div>
                  <div className="text-[11px] text-[#8B968D] mt-0.5">
                    Test RBAC permissions & view changes across roles
                  </div>
                </div>

                {sampleUsers.map((u) => {
                  const isCurrent = user?.id === u.id;
                  return (
                    <button
                      key={u.id}
                      onClick={() => {
                        switchUser(u);
                        setUserDropdownOpen(false);
                      }}
                      className={`w-full flex items-center space-x-2.5 px-3 py-2 text-xs hover:bg-[#FAF5EE] transition-colors ${
                        isCurrent ? "bg-[#FAF5EE] font-semibold" : ""
                      }`}
                    >
                      <img
                        src={u.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"}
                        alt={u.full_name}
                        className="w-7 h-7 rounded-full object-cover"
                      />
                      <div className="flex-1 text-left">
                        <div className="flex items-center space-x-1.5">
                          <span className="text-[#222B25]">{u.full_name}</span>
                          <span
                            className={`text-[9px] px-1.5 py-0.2 rounded font-medium ${
                              u.role === "Manager"
                                ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                                : u.role === "Departing"
                                ? "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
                                : u.role === "Incoming"
                                ? "bg-[#EFF3ED] text-[#4E5D52] border border-[#A6B29C]"
                                : "bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF]"
                            }`}
                          >
                            {u.role}
                          </span>
                        </div>
                        <div className="text-[10px] text-[#8B968D]">{u.title}</div>
                      </div>
                      {isCurrent && <CheckCircle2 className="w-4 h-4 text-[#4E5D52]" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Mobile Menu Button (only visible on mobile screens) */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] text-[#4E5D52] hover:bg-[#F2EADB] transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer (only shown when toggled on small screens) */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E5D5BF] bg-[#FAF5EE] p-3 space-y-1">
          {mobileNavLinks.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (setActiveTab) setActiveTab(item.id);
                  setMobileMenuOpen(false);
                }}
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
      )}
    </header>
  );
}
