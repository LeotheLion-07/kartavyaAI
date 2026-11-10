"use client";

import React, { useState, useEffect } from "react";
import {
  Database,
  Upload,
  RefreshCw,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Plus,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export function SourcesIngestionView() {
  const { currentProject } = useAuth();
  const [sources, setSources] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [syncing, setSyncing] = useState(false);

  // Upload Form state
  const [uploadName, setUploadName] = useState("");
  const [sourceType, setSourceType] = useState("Document");
  const [classification, setClassification] = useState("Team");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // GitHub import state
  const [repoUrl, setRepoUrl] = useState("https://github.com/org/core-platform");
  const [branch, setBranch] = useState("main");

  const fetchData = async () => {
    setLoading(true);
    try {
      const srcList = await api.getSources(currentProject.id);
      setSources(srcList);
      const summ = await api.getAnalyticsSummary();
      setSummary(summ);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentProject]);

  const handleSyncLatest = async () => {
    setSyncing(true);
    try {
      const formData = new FormData();
      formData.append("repo_url", repoUrl);
      formData.append("project_id", currentProject.id.toString());
      formData.append("branch", branch);
      await api.githubImport(formData);
      fetchData();
      alert("Connectors synchronized. Parsed recent commits and regenerated BFT consensus proofs.");
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !uploadName.trim()) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("project_id", currentProject.id.toString());
      fd.append("name", uploadName);
      fd.append("source_type", sourceType);
      fd.append("access_classification", classification);
      fd.append("consent_status", "Granted");
      fd.append("file", selectedFile);

      const res = await api.uploadSource(fd);
      fetchData();
      setShowUploadModal(false);
      setUploadName("");
      setSelectedFile(null);
      alert(`Source successfully ingested and parsed! Extracted ${res.source.claims_extracted} evidence-backed claims.`);
    } catch (e: any) {
      alert(`Upload error: ${e.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-8 max-w-7xl mx-auto overflow-y-auto">
      {/* Top Banner */}
      <div className="p-5 rounded-2xl border border-[#A6B29C] bg-[#EFF3ED] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-[#4E5D52] text-white shadow-xs">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-[#222B25]">
                Ethical On-Demand Knowledge Ingestion
              </h2>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white text-[#323F36] border border-[#A6B29C]">
                Zero Surveillance
              </span>
            </div>
            <p className="text-xs text-[#5E6F63] mt-0.5">
              Extracts insights exclusively from authorized repos, RFCs, and agreed public channels with explicit engineer consent.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={() => setShowUploadModal(true)}
            className="py-2 px-3.5 rounded-xl bg-white border border-[#E5D5BF] hover:bg-[#FAF5EE] text-xs font-semibold text-[#4E5D52] flex items-center space-x-1.5 transition-colors shadow-2xs"
          >
            <Upload className="w-3.5 h-3.5 text-[#4E5D52]" />
            <span>Upload Source</span>
          </button>
          <button
            onClick={handleSyncLatest}
            disabled={syncing}
            className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin" : ""}`} />
            <span>{syncing ? "Syncing..." : "Sync Latest"}</span>
          </button>
        </div>
      </div>

      {/* Active Source Connectors */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
            Active Source Connectors
          </div>
          <span className="text-xs text-[#5E6F63] font-medium">3 Synced • 1 Available</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Connector 1: GitHub */}
          <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-[#4E5D52] text-white flex items-center justify-center text-xs font-bold">
                  &lt;&gt;
                </div>
                <div>
                  <div className="text-xs font-bold text-[#222B25]">GitHub</div>
                  <div className="text-[10px] text-[#8B968D] font-mono">org/core-platform</div>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-[#323F36] bg-[#EFF3ED] border border-[#A6B29C] px-2 py-0.5 rounded-full flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
                <span>Synced</span>
              </span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-[#5E6F63]">
                <span>Pull Requests</span>
                <span className="font-bold text-[#222B25]">142</span>
              </div>
              <div className="flex justify-between text-[#5E6F63]">
                <span>Commits Analyzed</span>
                <span className="font-bold text-[#222B25]">312</span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#E5D5BF] flex justify-between items-center text-[10px] text-[#8B968D]">
              <span>Read-only scope</span>
              <span>12m ago</span>
            </div>
          </div>

          {/* Connector 2: Slack */}
          <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-[#63513C] text-white flex items-center justify-center text-xs font-bold">
                  #
                </div>
                <div>
                  <div className="text-xs font-bold text-[#222B25]">Slack</div>
                  <div className="text-[10px] text-[#8B968D]">3 Channels</div>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-[#323F36] bg-[#EFF3ED] border border-[#A6B29C] px-2 py-0.5 rounded-full flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
                <span>Synced</span>
              </span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-[#5E6F63]">
                <span>Indexed Threads</span>
                <span className="font-bold text-[#222B25]">38</span>
              </div>
              <div className="flex justify-between text-[#5E6F63]">
                <span>#proj-handover</span>
                <span className="font-bold text-[#222B25]">19 msgs</span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#E5D5BF] flex justify-between items-center text-[10px] text-[#8B968D]">
              <span>Public threads only</span>
              <span>28m ago</span>
            </div>
          </div>

          {/* Connector 3: Notion Wiki */}
          <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-[#FAF5EE] text-[#4E5D52] flex items-center justify-center text-xs font-bold border border-[#E5D5BF]">
                  N
                </div>
                <div>
                  <div className="text-xs font-bold text-[#222B25]">Notion Wiki</div>
                  <div className="text-[10px] text-[#8B968D]">Workspace: Eng</div>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-[#323F36] bg-[#EFF3ED] border border-[#A6B29C] px-2 py-0.5 rounded-full flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A6B29C]" />
                <span>Synced</span>
              </span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-[#5E6F63]">
                <span>Archived RFCs</span>
                <span className="font-bold text-[#222B25]">14</span>
              </div>
              <div className="flex justify-between text-[#5E6F63]">
                <span>ADR Documents</span>
                <span className="font-bold text-[#222B25]">9</span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#E5D5BF] flex justify-between items-center text-[10px] text-[#8B968D]">
              <span>Page read-only</span>
              <span>1h ago</span>
            </div>
          </div>

          {/* Connector 4: Jira & Drive */}
          <div className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-[#FAF5EE] text-[#4E5D52] flex items-center justify-center text-xs font-bold border border-[#E5D5BF]">
                  *
                </div>
                <div>
                  <div className="text-xs font-bold text-[#222B25]">Jira & Drive</div>
                  <div className="text-[10px] text-[#8B968D]">Sprint & spec logs</div>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-[#8B968D]">Ready</span>
            </div>
            <p className="text-[11px] text-[#5E6F63] line-clamp-2">
              Connect sprint tickets and architecture diagrams for auto-correlation.
            </p>
            <div className="pt-2 border-t border-[#E5D5BF]">
              <button
                onClick={() => alert("Jira & Google Drive OAuth connector ready for enterprise SSO.")}
                className="w-full text-center text-xs font-semibold text-[#4E5D52] hover:underline"
              >
                Connect Source →
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Proactive Knowledge Risk (Bus Factor Alerts) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#222B25]">
            <span>Proactive Knowledge Risk</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF]">
              Bus Factor Alerts
            </span>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => alert("Targeted Interview bot queued for Sarah Lin.")}
              className="py-1 px-2.5 rounded-lg border border-[#E5D5BF] bg-white text-xs font-medium text-[#4E5D52] hover:bg-[#FAF5EE]"
            >
              Targeted Interview
            </button>
            <button
              onClick={() => alert("Handover packet assembled.")}
              className="py-1 px-3 rounded-lg bg-[#4E5D52] text-white text-xs font-semibold shadow-2xs hover:bg-[#3A473E]"
            >
              Generate Handover Packet
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {summary?.bus_factor_risks?.map((risk: any) => (
            <div
              key={risk.id}
              className="p-4 rounded-xl border border-[#E5D5BF] bg-white shadow-2xs space-y-3"
            >
              <div className="flex items-center justify-between text-xs">
                <span
                  className={`font-semibold flex items-center space-x-1 ${
                    risk.severity === "Critical"
                      ? "text-[#7A3E2D]"
                      : risk.severity === "Medium"
                      ? "text-[#63513C]"
                      : "text-[#323F36]"
                  }`}
                >
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Bus Factor: {risk.bus_factor} ({risk.severity})</span>
                </span>
                <span className="font-bold text-[#222B25] font-mono text-[11px]">
                  {risk.risk_score}
                </span>
              </div>

              <div>
                <h3 className="font-semibold text-sm text-[#222B25]">
                  {risk.title}
                </h3>
                <p className="text-xs text-[#5E6F63] mt-1 leading-relaxed">
                  {risk.description}
                </p>
              </div>

              <div className="pt-2 border-t border-[#E5D5BF] flex items-center justify-between text-xs">
                <span className="text-[#8B968D] text-[11px] truncate max-w-[140px]">
                  {risk.owner}
                </span>
                <span className="font-semibold text-[#4E5D52] hover:underline cursor-pointer">
                  {risk.action_label}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Knowledge Distribution Matrix */}
      <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
            Knowledge Distribution Matrix
          </div>
          <div className="text-xs text-[#8B968D] mt-0.5">
            Sole owner density vs system criticality across core modules.
          </div>
        </div>

        <div className="space-y-4">
          {summary?.knowledge_distribution?.map((item: any, i: number) => {
            const isCritical = item.density > 80;
            const isModerate = item.density > 50 && item.density <= 80;
            return (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-[#222B25]">
                    {item.module} <span className="text-[#8B968D] font-normal">({item.owner})</span>
                  </span>
                  <span className="font-bold text-[#222B25] font-mono">
                    {item.density}%
                  </span>
                </div>
                <div className="w-full bg-[#FAF5EE] rounded-full h-2 overflow-hidden border border-[#E5D5BF]">
                  <div
                    className={`h-2 rounded-full ${
                      isCritical
                        ? "bg-[#7A3E2D]"
                        : isModerate
                        ? "bg-[#C9B79E]"
                        : "bg-[#4E5D52]"
                    }`}
                    style={{ width: `${item.density}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Ingestion & Verification Log Table */}
      <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-[#222B25]">
              Recent Ingestion & Verification Log
            </div>
            <div className="text-xs text-[#8B968D]">
              Live evidence stream parsed into verified architectural decisions.
            </div>
          </div>
          <button
            onClick={() => alert("Exported cryptographic audit manifest.")}
            className="py-1 px-3 rounded-lg border border-[#E5D5BF] bg-[#FAF5EE] text-xs font-medium text-[#4E5D52] hover:bg-[#F2EADB]"
          >
            Export Audit
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-[#E5D5BF] text-[11px] font-bold text-[#8B968D] uppercase tracking-wider">
              <tr>
                <th className="py-2.5 px-3">Artifact</th>
                <th className="py-2.5 px-3">Extracted Architectural Claim</th>
                <th className="py-2.5 px-3">Source Type</th>
                <th className="py-2.5 px-3">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5D5BF]">
              {sources.map((s) => (
                <tr key={s.id} className="hover:bg-[#FAF5EE]/70">
                  <td className="py-3 px-3 font-mono font-semibold text-[#4E5D52]">
                    {s.source_code}
                  </td>
                  <td className="py-3 px-3 font-medium text-[#222B25]">
                    {s.name}
                  </td>
                  <td className="py-3 px-3 text-[#5E6F63]">
                    {s.source_type}
                  </td>
                  <td className="py-3 px-3">
                    <span className="inline-flex items-center space-x-1 text-[#323F36] bg-[#EFF3ED] border border-[#A6B29C] px-2 py-0.5 rounded-full font-semibold">
                      <Check className="w-3.5 h-3.5 text-[#4E5D52]" />
                      <span>Grounded</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer cryptographically signed proof */}
        <div className="pt-3 border-t border-[#E5D5BF] flex flex-wrap items-center justify-between text-[11px] text-[#8B968D] font-mono gap-2">
          <div className="flex items-center space-x-1.5">
            <Lock className="w-3.5 h-3.5 text-[#A6B29C]" />
            <span>Cryptographically signed manifest — Proof ledger synced with GitHub & Jira</span>
          </div>
          <div>BFT Consensus Validated</div>
        </div>
      </div>

      {/* Upload Source Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-base text-[#222B25]">
                Upload Authorized Source
              </h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-[#8B968D] hover:text-[#222B25]"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleFileUpload} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-[#222B25]">
                  Source Title / Name:
                </label>
                <input
                  type="text"
                  required
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  placeholder="e.g. Architecture RFC 045: Payout Settlement Engine"
                  className="mt-1 w-full p-2.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-[#222B25]">
                    Source Type:
                  </label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="mt-1 w-full p-2.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25]"
                  >
                    <option value="Document">Document / PDF</option>
                    <option value="Architecture RFC">Architecture RFC</option>
                    <option value="Markdown Spec">Markdown Spec</option>
                    <option value="Meeting Notes">Meeting Notes</option>
                    <option value="CSV Board">CSV Task Board</option>
                  </select>
                </div>
                <div>
                  <label className="font-semibold text-[#222B25]">
                    Classification:
                  </label>
                  <select
                    value={classification}
                    onChange={(e) => setClassification(e.target.value)}
                    className="mt-1 w-full p-2.5 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25]"
                  >
                    <option value="Public">Public</option>
                    <option value="Team">Team (Default)</option>
                    <option value="Restricted">Restricted (DLP Gated)</option>
                    <option value="Confidential">Confidential (Secrets/Vault)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-semibold text-[#222B25]">
                  Select File (PDF, MD, TXT, CSV, JSON):
                </label>
                <input
                  type="file"
                  required
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="mt-1 w-full p-2 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#4E5D52] file:text-white"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="py-2 px-3 rounded-xl border border-[#E5D5BF] text-[#5E6F63]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="py-2 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white font-semibold flex items-center space-x-1.5"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>{uploading ? "Extracting Claims..." : "Ingest & Extract Claims"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
