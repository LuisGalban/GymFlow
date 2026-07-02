"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth } from "@/app/context/AuthContext";
import { api } from "@/app/context/AuthContext";
import { addPendingCheckin, getAllPendingCheckins, clearPendingCheckins } from "@/lib/idb";
import {
  Search, CheckCircle2, AlertTriangle, XCircle, UserCheck,
  Loader2, Clock, Phone, CreditCard,
} from "lucide-react";

interface MiembroResponse {
  id: number;
  cedula: string;
  nombre: string;
  telefono: string | null;
  estado_logico: boolean;
  estatus_actual: "activo" | "por_vencer" | "en_gracia" | "vencido" | null;
  dias_restantes_gracia: number | null;
}

type SemaforoColor = "activo" | "por_vencer" | "en_gracia" | "vencido";

const SEMAFORO = {
  activo: {
    clase: "semaphore-green",
    icon: CheckCircle2,
    label: "Acceso Permitido",
    sublabel: "Membresía al día",
    pulso: false,
  },
  por_vencer: {
    clase: "semaphore-amber",
    icon: AlertTriangle,
    label: "Por Vencer",
    sublabel: "Próximos 3 días",
    pulso: true,
  },
  en_gracia: {
    clase: "semaphore-amber",
    icon: Clock,
    label: "Período de Gracia",
    sublabel: "",
    pulso: true,
  },
  vencido: {
    clase: "semaphore-rose",
    icon: XCircle,
    label: "Acceso Bloqueado",
    sublabel: "Requiere pago inmediato",
    pulso: false,
  },
};

export default function ReceptionPage() {
  const { token } = useAuth();
  const [cedula, setCedula] = useState("");
  const [miembro, setMiembro] = useState<MiembroResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [checkinDone, setCheckinDone] = useState(false);
  const [error, setError] = useState("");

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    if (!cedula.trim()) return;
    setLoading(true);
    setMiembro(null);
    setError("");
    setCheckinDone(false);
    try {
      const res = await api.get(`/api/v1/members/search/${cedula.trim()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMiembro(res.data);
    } catch (err: unknown) {
      const e = err as { response?: { status?: number } };
      setError(e?.response?.status === 404 ? "No se encontró ningún miembro con esa cédula." : "Error al buscar. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  }

  async function registrarCheckin() {
    if (!miembro) return;
    setCheckinLoading(true);
    try {
      await api.post("/api/v1/asistencias/checkin",
        { miembro_id: miembro.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCheckinDone(true);
    } catch (err: any) {
      // Si la petición falla por falta de red, guardamos el check‑in en IndexedDB
      if (!err?.response) {
        await addPendingCheckin(miembro.id);
        setError("Sin conexión: se guardó el check‑in y se enviará cuando haya red.");
      } else {
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e?.response?.data?.detail || "No se pudo registrar la asistencia.");
      }
    } finally {
      setCheckinLoading(false);
    }
  }

  const estatus = miembro?.estatus_actual as SemaforoColor | null;

  // Sincronizar check‑ins pendientes al volver a estar online
  useEffect(() => {
    async function syncPending() {
      if (!navigator.onLine) return;
      const pending = await getAllPendingCheckins();
      if (pending.length === 0) return;
      try {
        await api.post(
          "/api/v1/asistencias/batch",
          { checkins: pending },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await clearPendingCheckins();
      } catch (e) {
        console.error("Error al sincronizar check‑ins pendientes", e);
      }
    }
    window.addEventListener("online", syncPending);
    syncPending();
    return () => window.removeEventListener("online", syncPending);
  }, [token]);
  const config = estatus ? SEMAFORO[estatus] : null;

  return (
    <DashboardLayout title="Control de Acceso — Recepción">
      <div className="max-w-2xl mx-auto flex flex-col gap-6">

        {/* Barra de búsqueda grande */}
        <form onSubmit={buscar} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
            <input
              id="reception-search"
              type="text"
              value={cedula}
              onChange={(e) => setCedula(e.target.value)}
              placeholder="Buscar por Cédula (ej. V-25111222)"
              className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 text-lg text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50 focus:bg-indigo-500/5 transition-all duration-200"
            />
          </div>
          <button
            id="reception-search-btn"
            type="submit"
            disabled={loading}
            className="px-6 py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all duration-200 flex items-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Buscar
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
            <XCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* Tarjeta del miembro con semáforo */}
        {miembro && config && (
          <div className={`kinetic-glass rounded-2xl p-6 flex flex-col gap-5 ${config.pulso ? "animate-pulse" : ""}`}>
            {/* Semáforo */}
            <div className={`flex items-center gap-3 px-5 py-4 rounded-xl ${config.clase}`}>
              <config.icon className="w-6 h-6 shrink-0" />
              <div>
                <p className="font-bold text-base">{config.label}</p>
                <p className="text-xs opacity-70">
                  {estatus === "en_gracia"
                    ? `${miembro.dias_restantes_gracia} día(s) restante(s) de gracia`
                    : config.sublabel}
                </p>
              </div>
            </div>

            {/* Datos del miembro */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">{miembro.nombre}</h2>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 text-sm text-white/50">
                  <CreditCard className="w-3.5 h-3.5" />
                  <span>{miembro.cedula}</span>
                </div>
                {miembro.telefono && (
                  <div className="flex items-center gap-2 text-sm text-white/50">
                    <Phone className="w-3.5 h-3.5" />
                    <span>{miembro.telefono}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Botón Check-in */}
            {estatus !== "vencido" && (
              <button
                id="checkin-btn"
                onClick={registrarCheckin}
                disabled={checkinLoading || checkinDone}
                className={`w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200
                  ${checkinDone
                    ? "bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 cursor-default"
                    : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20"
                  }`}
              >
                {checkinLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : checkinDone ? (
                  <><CheckCircle2 className="w-4 h-4" /> ¡Acceso Registrado!</>
                ) : (
                  <><UserCheck className="w-4 h-4" /> Registrar Entrada</>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
