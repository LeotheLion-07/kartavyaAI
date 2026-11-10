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

    // Load sample users & initial session
    const initAuth = async () => {
      try {
        const users = await api.getSampleUsers();
        setSampleUsers(users);

        const existingToken = getAuthToken();
        if (existingToken) {
          try {
            const me = await api.getMe();
            setUser(me);
          } catch {
            // Default to Alex Morgan (Manager) if token expired or demo mode
            if (users.length > 0) {
              const defaultUser = users[0]; // Alex Morgan
              setAuthToken(defaultUser.access_token);
              setUser(defaultUser);
            }
          }
        } else if (users.length > 0) {
          // Auto-sign in as Alex Morgan for instantaneous demo readiness
          const defaultUser = users[0];
          setAuthToken(defaultUser.access_token);
          setUser(defaultUser);
        }
      } catch (err) {
        console.error("Auth init error:", err);
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
