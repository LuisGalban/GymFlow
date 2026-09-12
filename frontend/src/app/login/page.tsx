"use client";

import { useState } from "react";
import { useAuth } from "@/app/context/AuthContext";
import {
  Dumbbell,
  Mail,
  Lock,
  Loader2,
  AlertCircle,
  UserRound,
  KeyRound,
} from "lucide-react";

const DEMO_ACCOUNTS = [
  {
    label: "Administrador",
    correo: "admin@gymflow.com",
    password: "admin123",
  },
  {
    label: "Recepción",
    correo: "recepcion@gymflow.com",
    password: "worker123",
  },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(correo, password);
    } catch {
      setError("Correo o contraseña incorrectos. Verifica tus datos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Orbes decorativos de fondo */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-indigo-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-violet-600/10 blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/15 border border-indigo-400/20 flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/10">
            <Dumbbell className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">GymFlow Analytics</h1>
          <p className="text-sm text-white/40 mt-1">Accede a tu panel de gestión</p>
        </div>

        {/* Tarjeta de Login */}
        <form
          onSubmit={handleSubmit}
          className="kinetic-glass rounded-2xl p-8 flex flex-col gap-5"
        >
          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Correo */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase tracking-wider">
              Correo electrónico
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
              <input
                id="login-email"
                type="email"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                placeholder="admin@gymflow.com"
                required
                className="w-full bg-white/5 border border-white/8 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 focus:bg-indigo-500/5 transition-all duration-200"
              />
            </div>
          </div>

          {/* Contraseña */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase tracking-wider">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-white/5 border border-white/8 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 focus:bg-indigo-500/5 transition-all duration-200"
              />
            </div>
          </div>

          {/* Botón */}
          <button
            id="login-submit"
            type="submit"
            disabled={loading}
            className="mt-2 w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold text-white transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Iniciando sesión…</>
            ) : (
              "Iniciar sesión"
            )}
          </button>
        </form>

        {/* Cuentas demo */}
        <div className="kinetic-glass rounded-2xl mt-4 p-4">
          <p className="text-[11px] font-medium text-white/40 uppercase tracking-wider">
            Cuentas demo · clic para autocompletar
          </p>
          <div className="mt-3 flex flex-col gap-2">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                key={account.correo}
                type="button"
                onClick={() => {
                  setCorreo(account.correo);
                  setPassword(account.password);
                  setError("");
                }}
                className="flex items-center justify-between gap-3 rounded-xl border border-white/8 bg-white/5 px-3.5 py-2.5 text-left text-sm text-white/60 transition-all duration-200 hover:border-indigo-400/40 hover:bg-indigo-500/10 hover:text-white"
              >
                <span className="flex min-w-0 items-center gap-2.5">
                  <UserRound className="h-4 w-4 shrink-0 text-white/25" />
                  <span className="truncate font-medium">{account.label}</span>
                </span>
                <span className="flex shrink-0 items-center gap-1.5 font-mono text-[11px] text-white/35">
                  <KeyRound className="h-3 w-3 text-white/20" />
                  {account.correo} / {account.password}
                </span>
              </button>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-white/20 mt-6">
          GymFlow Analytics © 2026 · Maracaibo, Zulia
        </p>
      </div>
    </div>
  );
}
