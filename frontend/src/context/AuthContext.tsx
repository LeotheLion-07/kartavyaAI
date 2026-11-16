"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { api, setAuthToken, removeAuthToken, getAuthToken } from "@/lib/api";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  title: string;
  department: string;
  avatar_url?: string;
  access_token?: string;
}

interface Project {
  id: number;
  name: string;
  slug: string;
  description?: string;
  bus_factor_score?: number;
}

interface AuthContextType {
  user: User | null;
  sampleUsers: User[];
  loading: boolean;
  theme: "light" | "dark";
  currentProject: Project;
  setCurrentProject: (proj: Project) => void;
  toggleTheme: () => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  switchUser: (targetUser: User) => void;
  refreshUser: () => Promise<void>;
}

const defaultProject: Project = {
  id: 1,
  name: "Core Platform & Payments",
  slug: "core-platform-payments",
  description: "High-throughput payment settlement engine (4,500 req/s), pgvector HNSW ledger",
  bus_factor_score: 1.0,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [sampleUsers, setSampleUsers] = useState<User[]>([]);
  const [currentProject, setCurrentProject] = useState<Project>(defaultProject);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Strictly light theme as requested
    localStorage.setItem("kartavya_theme", "light");
    document.documentElement.classList.remove("dark");

    // Load sample users & initial session with serverless cold-start retry & fallback resilience
    const initAuth = async (isRetry = false) => {
      try {
        const users = await api.getSampleUsers();
        if (users && users.length > 0) {
          setSampleUsers(users);

          const existingToken = getAuthToken();
          if (existingToken) {
            try {
              const me = await api.getMe();
              setUser(me);
            } catch {
              const defaultUser = users[0];
              setAuthToken(defaultUser.access_token || "");
              setUser(defaultUser);
            }
          } else {
            const defaultUser = users[0];
            setAuthToken(defaultUser.access_token || "");
            setUser(defaultUser);
          }
        }
      } catch (err) {
        console.warn("Auth initialization notice:", err);
        if (!isRetry) {
          // Retry once after 1.5s to handle serverless cold boot
          setTimeout(() => initAuth(true), 1500);
          return;
        }
        // Fallback demo users for graceful UI rendering during backend maintenance
        const fallbackUsers: User[] = [
          {
            id: 1,
            email: "alex.morgan@company.internal",
            full_name: "Alex Morgan",
            role: "Manager",
            title: "Engineering Manager",
            department: "Core Payments",
            avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
          },
          {
            id: 2,
            email: "sarah.lin@company.internal",
            full_name: "Sarah Lin",
            role: "Staff Engineer (Departing)",
            title: "Staff Lead L6",
            department: "Core Payments",
            avatar_url: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
          },
          {
            id: 3,
            email: "marcus.vance@company.internal",
            full_name: "Marcus Vance",
            role: "Successor",
            title: "Senior L5 Successor",
            department: "Core Payments",
            avatar_url: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
          },
        ];
        setSampleUsers(fallbackUsers);
        setUser(fallbackUsers[0]);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const toggleTheme = () => {
    // Project is kept strictly in light theme
    setTheme("light");
    localStorage.setItem("kartavya_theme", "light");
    document.documentElement.classList.remove("dark");
  };

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    setAuthToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    removeAuthToken();
    setUser(null);
  };

  const switchUser = (targetUser: User) => {
    if (targetUser.access_token) {
      setAuthToken(targetUser.access_token);
    }
    setUser(targetUser);
  };

  const refreshUser = async () => {
    try {
      const me = await api.getMe();
      setUser(me);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        sampleUsers,
        loading,
        theme,
        currentProject,
        setCurrentProject,
        toggleTheme,
        login,
        logout,
        switchUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
