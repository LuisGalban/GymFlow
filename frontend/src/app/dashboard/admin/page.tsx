"use client"

import { useEffect, useState } from "react"
import { api, useAuth } from "@/app/context/AuthContext"
import { useRouter } from "next/navigation"
import DashboardLayout from "@/app/components/DashboardLayout"
import { Loader2, AlertCircle, BarChart3, TrendingUp, CreditCard, Users } from "lucide-react"

interface KpiData {
  ingresos_netos_usd: number
  atletas_activos: number
  alertas_vencidos: number
}

interface Pago {
  id: number
  monto_usd: number
  fecha_pago: string
  referencia?: string
}

export default function AdminDashboardPage() {
  const { token, user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const [kpis, setKpis] = useState<KpiData | null>(null)
  const [pagos, setPagos] = useState<Pago[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // Protección de ruta RBAC: Solo Administradores
  useEffect(() => {
    if (!authLoading) {
      if (!token || !user || user.rol !== "admin") {
        router.push("/dashboard/reception")
      }
    }
  }, [token, user, authLoading, router])

  useEffect(() => {
    if (authLoading || !token || !user || user.rol !== "admin") return

    async function fetchData() {
      try {
        const config = {
          headers: { Authorization: `Bearer ${token}` }
        }
        const [kpiRes, cashRes] = await Promise.all([
          api.get("/api/v1/admin/kpis", config),
          api.get("/api/v1/admin/cashflow", config),
        ])
        setKpis(kpiRes.data)
        setPagos(cashRes.data.pagos)
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Error al cargar datos admin")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [authLoading, token, user])

  if (authLoading || !token || !user || user.rol !== "admin") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    )
  }


  return (
    <DashboardLayout title="Panel Administrador">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        {error && (
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : (
          <> {
            kpis && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="kinetic-glass p-5 rounded-xl flex flex-col items-center text-center">
                  <BarChart3 className="w-6 h-6 text-indigo-400 mb-2" />
                  <p className="text-sm text-white/60">Ingresos Netos (USD)</p>
                  <p className="text-xl font-bold text-white">${Number(kpis.ingresos_netos_usd).toFixed(2)}</p>
                </div>
                <div className="kinetic-glass p-5 rounded-xl flex flex-col items-center text-center">
                  <Users className="w-6 h-6 text-indigo-400 mb-2" />
                  <p className="text-sm text-white/60">Atletas Activos</p>
                  <p className="text-xl font-bold text-white">{kpis.atletas_activos}</p>
                </div>
                <div className="kinetic-glass p-5 rounded-xl flex flex-col items-center text-center">
                  <AlertCircle className="w-6 h-6 text-rose-400 mb-2" />
                  <p className="text-sm text-white/60">Alertas Vencidas</p>
                  <p className="text-xl font-bold text-white">{kpis.alertas_vencidos}</p>
                </div>
              </div>
            )
          }</>
        )}

        {/* Cashflow table */}
        {!loading && pagos.length > 0 && (
          <div className="kinetic-glass rounded-2xl overflow-hidden mt-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-white/30 text-xs uppercase tracking-wider">
                  <th className="px-4 py-2 font-medium">#</th>
                  <th className="px-4 py-2 font-medium">Monto USD</th>
                  <th className="px-4 py-2 font-medium">Fecha</th>
                  <th className="px-4 py-2 font-medium">Referencia</th>
                </tr>
              </thead>
              <tbody>
                {pagos.map((p) => (
                  <tr key={p.id} className="border-b border-white/4 hover:bg-white/2 transition-all duration-200">
                    <td className="px-4 py-2 text-white/70">{p.id}</td>
                    <td className="px-4 py-2 text-white">${Number(p.monto_usd).toFixed(2)}</td>
                    <td className="px-4 py-2 text-white/50">{new Date(p.fecha_pago).toLocaleString()}</td>
                    <td className="px-4 py-2 text-white/50">{p.referencia ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
