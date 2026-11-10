"use client";

import React, { useState, useEffect } from "react";
import {
  History,
  ShieldCheck,
  Search,
  Lock,
  CheckCircle2,
} from "lucide-react";
import { api } from "@/lib/api";

export function AuditLogsView() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedLog, setSelectedLog] = useState<any | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.getAuditLogs();
      setLogs(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((l) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      l.action?.toLowerCase().includes(q) ||
      l.user_name?.toLowerCase().includes(q) ||
      l.entity_type?.toLowerCase().includes(q) ||
      l.entity_id?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5D5BF] pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-[#222B25]">
              Immutable Security Audit Ledger
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]">
              Tamper-Evident
            </span>
          </div>
          <p className="text-xs text-[#5E6F63] mt-1">
            Cryptographic ledger tracking all knowledge ingestion, review board edits, DLP events, and cutover receipts.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#8B968D] absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audit trail..."
              className="pl-8 pr-3 py-1.5 rounded-lg border border-[#E5D5BF] bg-white text-xs text-[#222B25] w-56 focus:ring-1 focus:ring-[#4E5D52] focus:outline-hidden"
            />
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="p-5 rounded-2xl border border-[#E5D5BF] bg-white shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-[#E5D5BF] text-[11px] font-bold text-[#8B968D] uppercase tracking-wider">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Actor</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Target Entity</th>
                <th className="py-2.5 px-3">Cryptographic Proof / Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5D5BF] font-mono text-[11px]">
              {filteredLogs.map((log) => (
                <tr
                  key={log.id}
                  onClick={() => setSelectedLog(log)}
                  className="hover:bg-[#FAF5EE] cursor-pointer"
                >
                  <td className="py-3 px-3 text-[#5E6F63]">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-3 font-semibold text-[#222B25] font-sans">
                    {log.user_name}{" "}
                    <span className="text-[10px] text-[#8B968D] font-normal">({log.user_role})</span>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded font-bold text-[10px] ${
                        log.action?.includes("PUBLISH") || log.action?.includes("ACK")
                          ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                          : log.action?.includes("CONFLICT")
                          ? "bg-[#FAF5EE] text-[#63513C] border border-[#C9B79E]"
                          : "bg-[#FAF5EE] text-[#4E5D52] border border-[#E5D5BF]"
                      }`}
                    >
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-[#5E6F63]">
                    {log.entity_type} {log.entity_id ? `(${log.entity_id})` : ""}
                  </td>
                  <td className="py-3 px-3 text-[#8B968D] truncate max-w-[200px]">
                    {JSON.stringify(log.details_json || {})}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* JSON Payload Inspector Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-[#E5D5BF] pb-3">
              <div>
                <h3 className="font-bold text-sm text-[#222B25]">
                  Audit Log Inspector • Event #{selectedLog.id}
                </h3>
                <div className="text-[11px] text-[#5E6F63]">
                  {selectedLog.action} by {selectedLog.user_name}
                </div>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-[#8B968D] hover:text-[#222B25]"
              >
                ✕
              </button>
            </div>

            <pre className="p-3.5 rounded-xl bg-[#28322B] text-[#EFF3ED] text-xs font-mono overflow-x-auto border border-[#3A473E]">
              <code>{JSON.stringify(selectedLog, null, 2)}</code>
            </pre>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="py-1.5 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
