"use client";

import React, { useState } from "react";
import { useAuth, User } from "@/context/AuthContext";
import {
  ShieldCheck,
  CheckCircle2,
  ChevronDown,
  Layers,
  Sparkles,
} from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  gapsCount?: number;
}

export function Header({ activeTab, setActiveTab, gapsCount = 3 }: HeaderProps) {
  const { user, sampleUsers, switchUser, currentProject, setCurrentProject } = useAuth();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);

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

  const navItems = [
    { id: "timeline", label: "Timeline" },
    { id: "evidence", label: "Evidence Board" },
    { id: "role-handover", label: "Role Handover" },
    { id: "sources", label: "Sources & Ingestion" },
    { id: "gaps", label: "Knowledge Gaps", badge: gapsCount },
    { id: "chat", label: "Grounded Q&A" },
    { id: "audit", label: "Audit Logs" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#E5D5BF] bg-white/95 backdrop-blur transition-colors">
      <div className="flex h-15 items-center justify-between px-4 sm:px-6">
        {/* Left: Brand & Scope */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[#4E5D52] flex items-center justify-center text-white shadow-xs font-semibold">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="font-bold text-lg tracking-tight text-[#222B25]">
                Kartavya AI
              </span>
              <span className="hidden md:inline-flex items-center text-xs px-2.5 py-0.5 rounded-full font-medium bg-[#FAF5EE] text-[#4E5D52] border border-[#E5D5BF]">
                Handover Vault v2.4
              </span>
            </div>
          </div>

          <div className="hidden lg:block h-5 w-[1px] bg-[#E5D5BF] mx-2" />

          {/* Project / Scope Switcher */}
          <div className="relative">
            <button
              onClick={() => setProjectDropdownOpen(!projectDropdownOpen)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] hover:bg-[#F2EADB] text-xs font-medium text-[#4E5D52] transition-colors"
            >
              <Layers className="w-3.5 h-3.5 text-[#4E5D52]" />
              <span className="truncate max-w-[170px] font-semibold">{currentProject.name}</span>
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

        {/* Center: Navigation Tabs */}
        <nav className="hidden xl:flex items-center space-x-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#4E5D52] text-white font-semibold shadow-xs"
                    : "text-[#5E6F63] hover:text-[#222B25] hover:bg-[#FAF5EE]"
                }`}
              >
                <span>{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`ml-1.5 inline-flex items-center justify-center px-1.5 py-0.2 text-[10px] font-bold rounded-full ${
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
        </nav>

        {/* Right: Status Badges & User Role Switcher */}
        <div className="flex items-center space-x-2 sm:space-x-3">
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
        </div>
      </div>
    </header>
  );
}
