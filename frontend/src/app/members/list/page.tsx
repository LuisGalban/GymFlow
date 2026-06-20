"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth, api } from "@/app/context/AuthContext";
import {
  Users, CheckCircle2, AlertTriangle, XCircle, Clock,
  Trash2, Loader2, Search,
} from "lucide-react";

interface Miembro {
  id: number;
  cedula: string;
  nombre: string;
  telefono: string | null;
  estado_logico: boolean;
  estatus_actual: "activo" | "por_vencer" | "en_gracia" | "vencido" | null;
  dias_restantes_gracia: number | null;
  plan_nombre: string | null; // Nombre del plan asociado
  plan_id: number | null; // ID del plan asociado
}

const EstatusChip = ({ estatus, dias }: { estatus: Miembro["estatus_actual"]; dias: number | null }) => {
  const map = {
    activo: { label: "Activo", cls: "semaphore-green", icon: CheckCircle2 },
    por_vencer: { label: "Por Vencer", cls: "semaphore-amber", icon: AlertTriangle },
    en_gracia: { label: `Gracia (${dias}d)`, cls: "semaphore-amber", icon: Clock },
    vencido: { label: "Vencido", cls: "semaphore-rose", icon: XCircle },
  };
  const cfg = estatus ? map[estatus] : map.vencido;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.cls}`}>
      <cfg.icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
};

export default function MembersListPage() {
  const { token, isAdmin } = useAuth();
  const [miembros, setMiembros] = useState<Miembro[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => { fetchMiembros(); }, []);

  async function fetchMiembros() {
    try {
      const res = await api.get("/api/v1/members", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMiembros(res.data);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number, nombre: string) {
    if (!confirm(`¿Eliminar lógicamente a ${nombre}? El historial se preserva.`)) return;
    setDeleting(id);
    try {
      await api.delete(`/api/v1/members/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMiembros((prev) =>
        prev.map((m) => (m.id === id ? { ...m, estado_logico: false } : m))
      );
    } finally {
      setDeleting(null);
    }
  }

  const filtered = miembros.filter(
    (m) =>
      m.nombre.toLowerCase().includes(search.toLowerCase()) ||
      m.cedula.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <DashboardLayout title="Lista de Atletas">
      <div className="flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
            <input
              id="members-search"
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por nombre o cédula…"
              className="w-full bg-white/5 border border-white/8 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 transition-all duration-200"
            />
          </div>
          <span className="text-xs text-white/30">
            {filtered.length} atleta(s)
          </span>
        </div>

        {/* Tabla */}
        <div className="kinetic-glass rounded-2xl overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-white/30">
              <Users className="w-10 h-10" />
              <p className="text-sm">No se encontraron atletas</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-white/30 text-xs uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Atleta</th>
                  <th className="text-left px-5 py-3 font-medium">Cédula</th>
                  <th className="text-left px-5 py-3 font-medium">Teléfono</th>
                  <th className="text-left px-5 py-3 font-medium">Plan</th>
                  <th className="text-left px-5 py-3 font-medium">Estado</th>
                  {isAdmin && <th className="px-5 py-3" />}
                </tr>
              </thead>
              <tbody>
                {filtered.map((m) => (
                  <tr
                    key={m.id}
                    className={`border-b border-white/4 hover:bg-white/2 transition-all duration-200
                      ${!m.estado_logico ? "opacity-40 pointer-events-none" : ""}`}
                  >
                    <td className="px-5 py-3 font-medium text-white/80">{m.nombre}</td>
                    <td className="px-5 py-3 text-white/40 font-mono text-xs">{m.cedula}</td>
                    <td className="px-5 py-3 text-white/40">{m.telefono || "—"}</td>
                    <td className="px-5 py-3 text-white/40">{m.plan_nombre ?? "—"}</td>
                    <td className="px-5 py-3">
                      <EstatusChip estatus={m.estatus_actual} dias={m.dias_restantes_gracia} />
                    </td>
                    {isAdmin && (
                      <td className="px-5 py-3 text-right">
                        {m.estado_logico && (
                          <button
                            id={`delete-member-${m.id}`}
                            onClick={() => handleDelete(m.id, m.nombre)}
                            disabled={deleting === m.id}
                            className="p-1.5 rounded-lg text-white/20 hover:text-rose-400 hover:bg-rose-500/10 transition-all duration-200"
                          >
                            {deleting === m.id
                              ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              : <Trash2 className="w-3.5 h-3.5" />}
                          </button>
                        )}
                      </td>
                    )}
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
