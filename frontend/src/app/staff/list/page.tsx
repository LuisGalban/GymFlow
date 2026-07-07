"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth, api } from "@/app/context/AuthContext";
import {
  Users, Loader2, Trash2, Search, UserPlus, Shield, Wrench, AlertTriangle,
} from "lucide-react";

interface StaffUser {
  id: number;
  cedula: string;
  nombre: string;
  correo: string;
  rol: "admin" | "worker";
  estado_logico: boolean;
}

export default function StaffListPage() {
  const { token, user, isAdmin, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [staff, setStaff] = useState<StaffUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && (!token || !user || !isAdmin)) {
      router.push("/dashboard/reception");
    }
  }, [token, user, isAdmin, authLoading, router]);

  const fetchStaff = useCallback(async () => {
    setError(null);
    try {
      const res = await api.get("/api/v1/users", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStaff(res.data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Error al cargar la lista de usuarios";
      setError(msg);
      setStaff([]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (authLoading || !token || !user || !isAdmin) return;
    fetchStaff();
  }, [authLoading, token, user, isAdmin, fetchStaff]);

  async function handleDeactivate(id: number, nombre: string) {
    if (!confirm(`¿Desactivar a ${nombre}? El usuario dejará de tener acceso al sistema.`)) return;
    setDeleting(id);
    try {
      await api.delete(`/api/v1/users/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStaff((prev) =>
        prev.map((u) => (u.id === id ? { ...u, estado_logico: false } : u))
      );
    } finally {
      setDeleting(null);
    }
  }

  const filtered = staff.filter(
    (u) =>
      u.nombre.toLowerCase().includes(search.toLowerCase()) ||
      u.cedula.toLowerCase().includes(search.toLowerCase()) ||
      u.correo.toLowerCase().includes(search.toLowerCase())
  );

  if (authLoading || !token || !user || !isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <DashboardLayout title="Gestión de Personal">
      <div className="flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por nombre, cédula o correo…"
              className="w-full bg-white/5 border border-white/8 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 transition-all duration-200"
            />
          </div>
          <button
            onClick={() => router.push("/staff/register")}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-all duration-200"
          >
            <UserPlus className="w-4 h-4" />
            Nuevo Recepcionista
          </button>
        </div>

        {/* Tabla */}
        <div className="kinetic-glass rounded-2xl overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-rose-300">
              <AlertTriangle className="w-10 h-10" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-white/30">
              <Users className="w-10 h-10" />
              <p className="text-sm">No se encontraron usuarios</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-white/30 text-xs uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Cédula</th>
                  <th className="text-left px-5 py-3 font-medium">Nombre</th>
                  <th className="text-left px-5 py-3 font-medium">Correo</th>
                  <th className="text-left px-5 py-3 font-medium">Rol</th>
                  <th className="text-left px-5 py-3 font-medium">Estado</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => (
                  <tr
                    key={u.id}
                    className={`border-b border-white/4 hover:bg-white/2 transition-all duration-200
                      ${!u.estado_logico ? "opacity-40 pointer-events-none" : ""}`}
                  >
                    <td className="px-5 py-3 text-white/40 font-mono text-xs">{u.cedula}</td>
                    <td className="px-5 py-3 font-medium text-white/80">{u.nombre}</td>
                    <td className="px-5 py-3 text-white/40">{u.correo}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        u.rol === "admin"
                          ? "bg-indigo-500/15 text-indigo-300 border border-indigo-400/20"
                          : "bg-amber-500/15 text-amber-300 border border-amber-400/20"
                      }`}>
                        {u.rol === "admin" ? (
                          <><Shield className="w-3 h-3" /> Admin</>
                        ) : (
                          <><Wrench className="w-3 h-3" /> Recepcionista</>
                        )}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        u.estado_logico
                          ? "bg-emerald-500/15 text-emerald-300 border border-emerald-400/20"
                          : "bg-rose-500/15 text-rose-300 border border-rose-400/20"
                      }`}>
                        {u.estado_logico ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right">
                      {u.estado_logico && (
                        <button
                          onClick={() => handleDeactivate(u.id, u.nombre)}
                          disabled={deleting === u.id}
                          className="p-1.5 rounded-lg text-white/20 hover:text-rose-400 hover:bg-rose-500/10 transition-all duration-200"
                        >
                          {deleting === u.id
                            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            : <Trash2 className="w-3.5 h-3.5" />}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
