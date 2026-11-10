const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("kartavya_token");
}

export function setAuthToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("kartavya_token", token);
  }
}

export function removeAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("kartavya_token");
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Auth
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; token_type: string; user: any }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  register: (data: any) =>
    request<{ access_token: string; token_type: string; user: any }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getMe: () => request<any>("/auth/me"),
  getSampleUsers: () => request<any[]>("/auth/sample-users"),

  // Projects
  getProjects: () => request<any[]>("/projects/"),
  getProject: (id: number) => request<any>(`/projects/${id}`),
  createProject: (data: any) =>
    request<any>("/projects/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateProject: (id: number, data: any) =>
    request<any>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteProject: (id: number) =>
    request<any>(`/projects/${id}`, {
      method: "DELETE",
    }),

  // Sources
  getSources: (projectId?: number) =>
    request<any[]>(`/sources/${projectId ? `?project_id=${projectId}` : ""}`),
  uploadSource: (formData: FormData) =>
    request<any>("/sources/upload", {
      method: "POST",
      body: formData,
    }),
  githubImport: (formData: FormData) =>
    request<any>("/sources/github-import", {
      method: "POST",
      body: formData,
    }),

  // Claims
  getClaims: (params?: { projectId?: number; status?: string; category?: string }) => {
    const query = new URLSearchParams();
    if (params?.projectId) query.append("project_id", params.projectId.toString());
    if (params?.status) query.append("evidence_status", params.status);
    if (params?.category) query.append("category", params.category);
    return request<{ claims: any[]; total_count: number; hidden_count: number }>(`/claims/?${query.toString()}`);
  },
  getClaim: (id: number) => request<any>(`/claims/${id}`),
  updateClaim: (id: number, data: any) =>
    request<any>(`/claims/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  confirmClaim: (id: number) =>
    request<any>(`/claims/${id}/confirm`, {
      method: "POST",
    }),

  // Decisions
  getDecisions: (params?: { projectId?: number; person?: string; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.projectId) query.append("project_id", params.projectId.toString());
    if (params?.person) query.append("person", params.person);
    if (params?.status) query.append("evidence_status", params.status);
    return request<any[]>(`/decisions/?${query.toString()}`);
  },
  createDecision: (data: any) =>
    request<any>("/decisions/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Conflicts
  getConflicts: (params?: { projectId?: number; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.projectId) query.append("project_id", params.projectId.toString());
    if (params?.status) query.append("resolution_status", params.status);
    return request<any[]>(`/conflicts/?${query.toString()}`);
  },
  resolveConflict: (id: number, data: { resolution_notes: string; accepted_fix?: string }) =>
    request<any>(`/conflicts/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Knowledge Gaps
  getGapQuestions: (params?: { projectId?: number; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.projectId) query.append("project_id", params.projectId.toString());
    if (params?.status) query.append("status", params.status);
    return request<any[]>(`/gaps/?${query.toString()}`);
  },
  answerGapQuestion: (id: number, data: { answer: string; respondent_name?: string }) =>
    request<any>(`/gaps/${id}/answer`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  createGapQuestion: (data: any) =>
    request<any>("/gaps/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Handovers & Role Views
  getHandoverCases: (projectId?: number) =>
    request<any[]>(`/handovers/cases${projectId ? `?project_id=${projectId}` : ""}`),
  getHandoverCase: (caseId: number) => request<any>(`/handovers/case/${caseId}`),
  getRoleView: (roleType: string, projectId: number) =>
    request<any>(`/handovers/role-view/${roleType}?project_id=${projectId}`),
  acknowledgeHandover: (caseId: number, data: { notes: string }) =>
    request<any>(`/handovers/case/${caseId}/acknowledge`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  approveHandover: (caseId: number) =>
    request<any>(`/handovers/case/${caseId}/approve`, {
      method: "POST",
    }),
  toggleTask: (taskId: number) =>
    request<any>(`/handovers/tasks/${taskId}/toggle`, {
      method: "PUT",
    }),

  // Grounded Chat
  queryChat: (data: { project_id: number; query: string }) =>
    request<{
      query: string;
      answer: string;
      is_grounded: boolean;
      evidence_count: number;
      citations: any[];
      redacted_items_count: number;
    }>("/chat/query", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Permissions & Access Requests
  getAccessRequests: (status?: string) =>
    request<any[]>(`/permissions/requests${status ? `?status=${status}` : ""}`),
  createAccessRequest: (data: { resource_type: string; resource_id: number; resource_name: string; reason?: string }) =>
    request<any>("/permissions/request", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  reviewAccessRequest: (id: number, data: { status: string; review_comment?: string }) =>
    request<any>(`/permissions/requests/${id}/review`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Audit Logs
  getAuditLogs: (action?: string) =>
    request<any[]>(`/audit/${action ? `?action=${action}` : ""}`),

  // Analytics & Dashboard Summary
  getAnalyticsSummary: () => request<any>("/analytics/summary"),
};
