"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth, api } from "@/app/context/AuthContext";
import {
  Building2, Loader2, Plus, Copy, Check, Pause, Play, Ban,
  AlertTriangle, DollarSign, Users,
} from "lucide-react";
import TableSkeleton from "@/app/components/TableSkeleton";

interface GymData {
  id: number;
  nombre: string;
  direccion: string;
  telefono: string | null;
  estado_suscripcion: string;
  token_sede: string | null;
  estado_logico: boolean;
  miembros_activos: number;
  ingresos_mensuales_usd: number;
}

export default function SuperAdminGymsPage() {
  const { token, user, isSuperAdmin, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [gyms, setGyms] = useState<GymData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newGymNombre, setNewGymNombre] = useState("");
  const [newGymDireccion, setNewGymDireccion] = useState("");
  const [creating, setCreating] = useState(false);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [togglingId, setTogglingId] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && (!token || !user || !isSuperAdmin)) {
      router.push("/login");
    }
  }, [token, user, isSuperAdmin, authLoading, router]);

  const fetchGyms = useCallback(async () => {
    setError(null);
    try {
      const res = await api.get("/api/v1/super-admin/gyms", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGyms(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al cargar sedes";
      setError(msg);
      setGyms([]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (authLoading || !token || !user || !isSuperAdmin) return;
    fetchGyms();
  }, [authLoading, token, user, isSuperAdmin, fetchGyms]);

  async function handleCreate() {
    if (!newGymNombre.trim() || !newGymDireccion.trim()) return;
    setCreating(true);
    try {
      await api.post(
        "/api/v1/super-admin/gyms",
        { nombre: newGymNombre.trim(), direccion: newGymDireccion.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreate(false);
      setNewGymNombre("");
      setNewGymDireccion("");
      fetchGyms();
    } finally {
      setCreating(false);
    }
  }

  async function handleToggleSubscription(gymId: number, currentState: string) {
    const newState = currentState === "activo" ? "pausado" : "activo";
    setTogglingId(gymId);
    try {
      await api.put(
        `/api/v1/super-admin/gyms/${gymId}/suscripcion`,
        { estado_suscripcion: newState },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setGyms((prev) =>
        prev.map((g) =>
          g.id === gymId ? { ...g, estado_suscripcion: newState } : g
        )
      );
    } finally {
      setTogglingId(null);
    }
  }

  function copyToken(tokenSede: string, gymId: number) {
    const url = `${window.location.origin}/register-gym/${tokenSede}`;
    navigator.clipboard.writeText(url);
    setCopiedId(gymId);
    setTimeout(() => setCopiedId(null), 2000);
  }

  if (authLoading || !token || !user || !isSuperAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <DashboardLayout title="Gestión de Sedes">
      <div className="flex flex-col gap-5">
        <div className="flex items-center justify-between gap-4">
          <p className="text-sm text-white/40">Administra las sedes del gimnasio</p>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-all duration-200"
          >
            <Plus className="w-4 h-4" />
            Nueva Sede
          </button>
        </div>

        {showCreate && (
          <div className="kinetic-glass rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-white/80 mb-4">Crear Nueva Sede</h3>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={newGymNombre}
                onChange={(e) => setNewGymNombre(e.target.value)}
                placeholder="Nombre del gimnasio"
                className="flex-1 bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 transition-all"
              />
              <input
                type="text"
                value={newGymDireccion}
                onChange={(e) => setNewGymDireccion(e.target.value)}
                placeholder="Dirección"
                className="flex-1 bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 transition-all"
              />
              <button
                onClick={handleCreate}
                disabled={creating || !newGymNombre.trim() || !newGymDireccion.trim()}
                className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold transition-all duration-200 flex items-center gap-2"
              >
                {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                Crear
              </button>
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/60 text-sm font-medium transition-all duration-200"
              >
                Cancelar
              </button>
            </div>
          </div>
        )}

        <div className="kinetic-glass rounded-2xl overflow-x-auto">
          {loading ? (
            <TableSkeleton rows={5} columns={6} />
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-rose-300">
              <AlertTriangle className="w-10 h-10" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          ) : gyms.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-white/30">
              <Building2 className="w-10 h-10" />
              <p className="text-sm">No hay sedes registradas</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-white/30 text-xs uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Sede</th>
                  <th className="text-left px-5 py-3 font-medium">Miembros</th>
                  <th className="text-left px-5 py-3 font-medium">Ingresos Mes</th>
                  <th className="text-left px-5 py-3 font-medium">Suscripción</th>
                  <th className="text-left px-5 py-3 font-medium">Token Onboarding</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody>
                {gyms.map((g) => (
                  <tr
                    key={g.id}
                    className="border-b border-white/4 hover:bg-white/2 transition-all duration-200"
                  >
                    <td className="px-5 py-3">
                      <p className="font-medium text-white/80">{g.nombre}</p>
                      <p className="text-xs text-white/30 mt-0.5">{g.direccion}</p>
                    </td>
                    <td className="px-5 py-3">
                      <span className="inline-flex items-center gap-1.5 text-white/50">
                        <Users className="w-3.5 h-3.5" />
                        {g.miembros_activos}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className="inline-flex items-center gap-1.5 text-white/50">
                        <DollarSign className="w-3.5 h-3.5" />
                        {g.ingresos_mensuales_usd.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        g.estado_suscripcion === "activo"
                          ? "bg-emerald-500/15 text-emerald-300 border border-emerald-400/20"
                          : g.estado_suscripcion === "pausado"
                          ? "bg-amber-500/15 text-amber-300 border border-amber-400/20"
                          : "bg-rose-500/15 text-rose-300 border border-rose-400/20"
                      }`}>
                        {g.estado_suscripcion === "activo" ? "Activo" : g.estado_suscripcion === "pausado" ? "Pausado" : "Suspendido"}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {g.token_sede ? (
                        <button
                          onClick={() => copyToken(g.token_sede!, g.id)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/15 text-indigo-300 border border-indigo-400/20 text-xs font-medium hover:bg-indigo-500/25 transition-all"
                        >
                          {copiedId === g.id ? (
                            <><Check className="w-3 h-3" /> Copiado</>
                          ) : (
                            <><Copy className="w-3 h-3" /> Copiar Link</>
                          )}
                        </button>
                      ) : (
                        <span className="text-xs text-white/20">Registrado</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => handleToggleSubscription(g.id, g.estado_suscripcion)}
                        disabled={togglingId === g.id}
                        className="p-1.5 rounded-lg text-white/20 hover:text-white/60 hover:bg-white/5 transition-all duration-200"
                        title={g.estado_suscripcion === "activo" ? "Pausar" : "Reanudar"}
                      >
                        {togglingId === g.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : g.estado_suscripcion === "activo" ? (
                          <Pause className="w-3.5 h-3.5" />
                        ) : (
                          <Play className="w-3.5 h-3.5" />
                        )}
                      </button>
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
