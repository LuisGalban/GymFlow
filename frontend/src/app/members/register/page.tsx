"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth, api } from "@/app/context/AuthContext";
import { Loader2, AlertCircle, UserPlus, CreditCard, CheckCircle2 } from "lucide-react";

export default function RegisterMemberPage() {
  const { token } = useAuth();
  const [cedula, setCedula] = useState("");
  const [nombre, setNombre] = useState("");
  const [telefono, setTelefono] = useState("");
  const [plans, setPlans] = useState<any[]>([]);
  const [planId, setPlanId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Fetch available plans on mount
  useEffect(() => {
    if (!token) return;
    api
      .get("/api/v1/planes", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => setPlans(res.data))
      .catch(() => setPlans([]));
  }, [token]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!planId) {
      setError("Debe seleccionar un plan inicial para el atleta.");
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await api.post(
        "/api/v1/members",
        { cedula, nombre, telefono, plan_id: Number(planId) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess("Atleta registrado exitosamente.");
      // Reset form
      setCedula("");
      setNombre("");
      setTelefono("");
      setPlanId("");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Error al registrar el atleta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <DashboardLayout title="Registro de Atleta">
      <div className="max-w-2xl mx-auto">
        <form
          onSubmit={handleSubmit}
          className="kinetic-glass rounded-2xl p-8 flex flex-col gap-6"
        >
          {error && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
          {success && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
              <CheckCircle2 className="w-4 h-4" />
              {success}
            </div>
          )}
          {/* Cedula */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Cédula (V‑...)</label>
            <input
              type="text"
              value={cedula}
              onChange={(e) => setCedula(e.target.value)}
              required
              placeholder="V‑25111222"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Nombre */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Nombre completo</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              required
              placeholder="Juan Pérez"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Telefono */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Teléfono (opcional)</label>
            <input
              type="text"
              value={telefono}
              onChange={(e) => setTelefono(e.target.value)}
              placeholder="0414‑1234567"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Seleccionar Plan Inicial */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Plan Inicial</label>
            <select
              value={planId}
              onChange={(e) => setPlanId(e.target.value)}
              required
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-400/50"
            >
              <option value="">Seleccione un plan</option>
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.nombre} - ${plan.precio_usd} ({plan.duracion_dias} días)
                </option>
              ))}
            </select>
          </div>
          {/* Botón */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Registrando…</>
            ) : (
              <>Registrar Atleta <UserPlus className="w-4 h-4" /></>
            )}
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
