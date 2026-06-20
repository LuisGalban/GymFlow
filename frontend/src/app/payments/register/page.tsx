"use client"

import { useState, useEffect } from "react"
import DashboardLayout from "@/app/components/DashboardLayout"
import { useAuth, api } from "@/app/context/AuthContext"
import { Loader2, AlertCircle, CreditCard, CheckCircle2, DollarSign } from "lucide-react"

// Helper to format error objects from Axios / validation
function formatError(err: any): string {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    // Join possible validation messages
    return detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
  }
  if (typeof detail === 'string') return detail;
  return err?.message || 'Error al registrar el pago.';
}

export default function RegisterPaymentPage() {
  const { token } = useAuth()
  const [monto, setMonto] = useState("")
  const [referencia, setReferencia] = useState("")
  const [tasaUsd, setTasaUsd] = useState("") // tasa de conversión local -> USD
  const [cedula, setCedula] = useState("") // Cédula del miembro
  const [plans, setPlans] = useState<any[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<number | "">("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // Fetch available plans on mount
  useEffect(() => {
    if (!token) return
    api
      .get("/api/v1/planes", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => setPlans(res.data))
      .catch(() => setPlans([]))
  }, [token])

  const montoNumber = parseFloat(monto) || 0
  const tasaNumber = parseFloat(tasaUsd) || 0
  const totalUsd = tasaNumber ? (montoNumber / tasaNumber).toFixed(2) : ""

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedPlanId) {
        setError('Debe seleccionar un plan antes de registrar el pago')
        return
    }
    setLoading(true)
    setError('')
    setSuccess('')
    try {
        await api.post(
            '/api/v1/payments/by-cedula',
            {
                cedula,
                planSeleccionado_id: selectedPlanId,
                monto_original: montoNumber,
                referencia,
                tasa_cambio: tasaNumber,
            },
            { headers: { Authorization: `Bearer ${token}` } }
        )
        setSuccess('Pago registrado exitosamente.')
        setMonto('')
        setReferencia('')
        setTasaUsd('')
        setCedula('')
        setSelectedPlanId('')
    } catch (err: any) {
        setError(formatError(err))
    } finally {
        setLoading(false)
    }
}

  return (
    <DashboardLayout title="Registro de Pago">
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
           {/* Seleccionar Plan */}
           <div className="flex flex-col gap-1.5">
             <label className="text-xs font-medium text-white/50 uppercase">Plan</label>
             <select
               value={selectedPlanId}
               onChange={(e) => setSelectedPlanId(Number(e.target.value) || "")}
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
          {/* Cédula del Miembro */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Cédula del Miembro</label>
            <input
              type="text"
              value={cedula}
              onChange={(e) => setCedula(e.target.value)}
              required
              placeholder="Ej. V-25111222"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Monto */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Monto (Moneda Local)</label>
            <input
              type="number"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              required
              placeholder="1000"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Tasa USD */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Tasa de Conversión a USD</label>
            <input
              type="number"
              step="any"
              value={tasaUsd}
              onChange={(e) => setTasaUsd(e.target.value)}
              required
              placeholder="24.50"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* Referencia */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Referencia (Pago Móvil)</label>
            <input
              type="text"
              value={referencia}
              onChange={(e) => setReferencia(e.target.value)}
              required
              placeholder="REF123456"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
          </div>
          {/* USD Calculado */}
          {totalUsd && (
            <div className="text-sm text-white/70">
              <DollarSign className="inline w-4 h-4 mr-1" />
              Aproximado en USD: <span className="font-medium text-white">${totalUsd}</span>
            </div>
          )}
          {/* Botón */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Registrando…</>
            ) : (
              <><span>Registrar Pago</span> <CreditCard className="w-4 h-4" /></>
            )}
          </button>
        </form>
      </div>
    </DashboardLayout>
  )
}
