"use client";

import React, { useState, useEffect } from "react";
import { X, Lock, Key, ShieldCheck, CheckCircle2, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface AccessRequestModalProps {
  onClose: () => void;
  resourceId?: number;
  resourceName?: string;
  onRequestSubmitted?: () => void;
}

export function AccessRequestModal({
  onClose,
  resourceId = 6,
  resourceName = "Failover Switch Routine & Breakglass Vault Tokens (#CLM-1065)",
  onRequestSubmitted,
}: AccessRequestModalProps) {
  const { user } = useAuth();
  const [reason, setReason] = useState(
    "Require access to breakglass vault credentials to verify on-call cutover readiness."
  );
  const [submitting, setSubmitting] = useState(false);
  const [pendingRequests, setPendingRequests] = useState<any[]>([]);
  const isManagerOrAdmin = user?.role === "Manager" || user?.role === "Admin";

  const fetchRequests = async () => {
    try {
      const res = await api.getAccessRequests();
      setPendingRequests(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleSubmitRequest = async () => {
    setSubmitting(true);
    try {
      await api.createAccessRequest({
        resource_type: "Claim",
        resource_id: resourceId,
        resource_name: resourceName,
        reason: reason,
      });
      fetchRequests();
      if (onRequestSubmitted) onRequestSubmitted();
      alert("Access request logged and routed to Alex Morgan (Eng Manager).");
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReview = async (requestId: number, status: "Approved" | "Rejected") => {
    try {
      await api.reviewAccessRequest(requestId, {
        status,
        review_comment: `Access ${status.toLowerCase()} by ${user?.full_name}`,
      });
      fetchRequests();
      if (onRequestSubmitted) onRequestSubmitted();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs animate-in fade-in">
      <div className="w-full max-w-xl bg-white rounded-2xl border border-[#E5D5BF] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#E5D5BF] flex items-center justify-between bg-[#FAF5EE]">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF]">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-mono font-semibold text-[#63513C]">
                SECURITY & DLP POLICY GATE
              </span>
              <h2 className="text-base font-bold text-[#222B25]">
                Permission-Aware Access Control
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
          {/* Request Form */}
          <div className="space-y-3">
            <div className="text-xs font-semibold text-[#8B968D] uppercase tracking-wider">
              Request Elevated Access
            </div>
            <div className="p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs">
              <div className="text-[#8B968D]">Resource:</div>
              <div className="font-semibold text-[#222B25] mt-0.5">
                {resourceName}
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-[#222B25]">
                Business Justification:
              </label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="mt-1 w-full p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs text-[#222B25] focus:ring-2 focus:ring-[#4E5D52] focus:outline-hidden"
              />
            </div>

            <button
              onClick={handleSubmitRequest}
              disabled={submitting}
              className="w-full py-2.5 px-4 rounded-xl bg-[#4E5D52] hover:bg-[#3A473E] text-white text-xs font-semibold shadow-xs transition-colors flex items-center justify-center space-x-1.5"
            >
              <Key className="w-4 h-4" />
              <span>{submitting ? "Submitting..." : "Submit Access Request to Manager"}</span>
            </button>
          </div>

          {/* Pending Requests List for Managers/Admins */}
          {isManagerOrAdmin && pendingRequests.length > 0 && (
            <div className="pt-4 border-t border-[#E5D5BF] space-y-3">
              <div className="text-xs font-semibold text-[#8B968D] uppercase tracking-wider flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-[#4E5D52]" />
                <span>Manager Approval Queue ({pendingRequests.length})</span>
              </div>
              <div className="space-y-2">
                {pendingRequests.map((req) => (
                  <div
                    key={req.id}
                    className="p-3 rounded-xl border border-[#E5D5BF] bg-[#FAF5EE] text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-[#222B25]">
                        {req.user_name}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          req.status === "Approved"
                            ? "bg-[#EFF3ED] text-[#323F36] border border-[#A6B29C]"
                            : req.status === "Rejected"
                            ? "bg-[#FAF0E6] text-[#7A3E2D] border border-[#E5D5BF]"
                            : "bg-white text-[#63513C] border border-[#C9B79E]"
                        }`}
                      >
                        {req.status}
                      </span>
                    </div>
                    <div className="text-[#5E6F63] text-[11px]">
                      {req.resource_name}
                    </div>
                    <div className="text-[11px] text-[#8B968D] italic">
                      "{req.reason}"
                    </div>

                    {req.status === "Pending" && (
                      <div className="flex space-x-2 pt-1">
                        <button
                          onClick={() => handleReview(req.id, "Approved")}
                          className="flex-1 py-1 px-2.5 rounded-lg bg-[#4E5D52] hover:bg-[#3A473E] text-white text-[11px] font-semibold flex items-center justify-center space-x-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve Access</span>
                        </button>
                        <button
                          onClick={() => handleReview(req.id, "Rejected")}
                          className="py-1 px-2.5 rounded-lg border border-[#E5D5BF] bg-white text-[#63513C] hover:bg-[#FAF0E6] text-[11px] font-medium flex items-center justify-center space-x-1"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Reject</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
