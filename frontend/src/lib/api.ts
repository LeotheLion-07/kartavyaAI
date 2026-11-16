/**
 * Resolves the backend API base URL dynamically:
 * 1. Explicit NEXT_PUBLIC_API_URL if configured in environment (e.g. Render/Railway backend URL or custom proxy).
 * 2. In browser environments:
 *    - If hostname is localhost or 127.0.0.1, connect directly to http://localhost:8000/api/v1 for local dev.
 *    - If deployed on Vercel or any public domain (e.g. *.vercel.app), use relative path "/api/v1".
 *      This routes requests to the current origin, leveraging Vercel rewrites and preventing
 *      Mixed Content (HTTPS -> HTTP) and CORS "Failed to fetch" errors.
 * 3. On SSR / Node: fallback to BACKEND_URL or http://localhost:8000/api/v1.
 */
export function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
  }

  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    const isLocalhost = hostname === "localhost" || hostname === "127.0.0.1";
    if (!isLocalhost) {
      return "/api/v1";
    }
  }

  if (process.env.BACKEND_URL) {
    return `${process.env.BACKEND_URL.replace(/\/+$/, "")}/api/v1`;
  }

  return "http://localhost:8000/api/v1";
}

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

  const base = getApiBase();
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${base}${cleanEndpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    return res.json();
  } catch (err: any) {
    if (err.name === "TypeError" && err.message?.toLowerCase().includes("fetch")) {
      const isLocal = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
      const hint = isLocal
        ? "Ensure the backend server is running on http://localhost:8000 (cd backend && python main.py)."
        : `Backend unreachable at ${url}. In Vercel Settings > Environment Variables, configure NEXT_PUBLIC_API_URL or verify your backend deployment.`;
      console.error(`[Kartavya AI Network Error] Failed to reach ${url}: ${err.message}. ${hint}`);
      throw new Error(`Failed to connect to backend API (${cleanEndpoint}). ${hint}`);
    }
    throw err;
  }
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
  detectConflicts: (projectId: number) =>
    request<any>(`/conflicts/detect?project_id=${projectId}`, {
      method: "POST",
    }),
  resolveConflict: (id: number, data: { resolution_notes: string; accepted_fix?: string; resolution_status?: string }) =>
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
  detectGaps: (projectId: number) =>
    request<any>(`/gaps/detect?project_id=${projectId}`, {
      method: "POST",
    }),
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
      has_conflict?: boolean;
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
