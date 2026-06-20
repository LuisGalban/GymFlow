"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem("gymflow_token");
    if (storedToken) {
      setToken(storedToken);
      axios.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
      fetchMe(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  async function fetchMe(t: string) {
    try {
      const res = await axios.get(`${API_BASE}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
      });
      setUser(res.data);
    } catch {
      localStorage.removeItem("gymflow_token");
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function login(correo: string, password: string) {
    const res = await axios.post(`${API_BASE}/api/v1/auth/login`, {
      correo,
      password,
    });
    const { access_token } = res.data;
    localStorage.setItem("gymflow_token", access_token);
    setToken(access_token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    await fetchMe(access_token);
    router.push("/dashboard/reception");
  }

  function logout() {
    localStorage.removeItem("gymflow_token");
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
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

// Cliente axios centralizado
export const api = axios.create({ baseURL: API_BASE });
