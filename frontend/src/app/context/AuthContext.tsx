"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface User {
  id: number;
  cedula: string;
  nombre: string;
  correo: string;
  rol: "admin" | "worker";
  estado_logico: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (correo: string, password: string) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

axios.defaults.withCredentials = true;

let isRestoring = false;

axios.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401 && !isRestoring) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    restoreSession();
  }, []);

  async function restoreSession() {
    isRestoring = true;
    try {
      const res = await axios.get(`${API_BASE}/api/v1/auth/session`, {
        withCredentials: true,
        validateStatus: (s) => s < 500,
      });
      if (res.status !== 200) {
        setUser(null);
        setToken(null);
        return;
      }
      const { user: userData, access_token } = res.data;
      setUser(userData);
      setToken(access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    } catch {
      setUser(null);
      setToken(null);
    } finally {
      isRestoring = false;
      setIsLoading(false);
    }
  }

  async function login(correo: string, password: string) {
    const res = await axios.post(
      `${API_BASE}/api/v1/auth/login`,
      { correo, password },
      { withCredentials: true }
    );
    const { access_token } = res.data;
    setToken(access_token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    const meRes = await axios.get(`${API_BASE}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    setUser(meRes.data);
    router.push("/dashboard/reception");
  }

  function logout() {
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
    window.location.href = "/login";
  }

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, logout, isAdmin: user?.rol === "admin" }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}

export const api = axios.create({ baseURL: API_BASE });

api.defaults.withCredentials = true;

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401 && !isRestoring) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
