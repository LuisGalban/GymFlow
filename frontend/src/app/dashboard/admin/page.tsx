"use client"

import { useEffect, useState } from "react"
import { api, useAuth } from "@/app/context/AuthContext"
import { useRouter } from "next/navigation"
import DashboardLayout from "@/app/components/DashboardLayout"
import Link from "next/link"
import { Loader2, AlertCircle, BarChart3, TrendingUp, CreditCard, Users, X } from "lucide-react"
import TableSkeleton from "@/app/components/TableSkeleton"

interface KpiData {
  ingresos_netos_usd: number
  atletas_activos: number
  alertas_vencidos: number
}

interface Vencido {
  id: number
  cedula: string
  nombre: string
  dias_vencido: number
  telefono?: string
}

interface Pago {
  id: number
  monto_usd: number
  fecha_pago: string
  referencia?: string
}

interface PagoDetalle {
  id: number
  membresia_miembro_id: number
  registrado_por: number
  monto_original: number
  moneda: string
  tasa_cambio: number
  monto_usd: number
  metodo_pago: string
  referencia?: string
  fecha_pago: string
  miembro_nombre: string
  miembro_cedula: string
  plan_nombre: string
  registrador_nombre: string
}

export default function AdminDashboardPage() {
  const { token, user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const [kpis, setKpis] = useState<KpiData | null>(null)
  const [pagos, setPagos] = useState<Pago[]>([])
  const [vencidos, setVencidos] = useState<Vencido[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [filtroRango, setFiltroRango] = useState("")
  const [filtroDesde, setFiltroDesde] = useState("")
  const [filtroHasta, setFiltroHasta] = useState("")
  const [selectedPayment, setSelectedPayment] = useState<PagoDetalle | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

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
        const params: Record<string, string> = {}
        if (filtroRango) params.rango = filtroRango
        if (filtroRango === "personalizado") {
          if (filtroDesde) params.desde = filtroDesde
          if (filtroHasta) params.hasta = filtroHasta
        }
        const config = {
          params,
          headers: { Authorization: `Bearer ${token}` }
        }
        const [kpiRes, cashRes, vencidosRes] = await Promise.all([
          api.get("/api/v1/admin/kpis", config),
          api.get("/api/v1/admin/cashflow", config),
          api.get("/api/v1/admin/vencidos", config),
        ])
        setKpis(kpiRes.data)
        setPagos(cashRes.data.pagos)
        setVencidos(vencidosRes.data)
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Error al cargar datos admin")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [authLoading, token, user, filtroRango, filtroDesde, filtroHasta])

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
        {/* Filtros temporales */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { key: "dia", label: "Hoy" },
            { key: "semana", label: "Esta Semana" },
            { key: "mes", label: "Este Mes" },
            { key: "ano", label: "Este Año" },
            { key: "personalizado", label: "Personalizado" },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => {
                setFiltroRango(key)
                if (key !== "personalizado") {
                  setFiltroDesde("")
                  setFiltroHasta("")
                }
                setLoading(true)
              }}
              className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all duration-200 ${
                filtroRango === key
                  ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                  : "bg-white/5 text-white/50 border border-white/10 hover:bg-white/10"
              }`}
            >
              {label}
            </button>
          ))}
          {filtroRango === "personalizado" && (
            <div className="flex items-center gap-2 ml-2">
              <input
                type="date"
                value={filtroDesde}
                onChange={(e) => { setFiltroDesde(e.target.value); setLoading(true) }}
                className="bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white/70"
              />
              <span className="text-white/30 text-xs">a</span>
              <input
                type="date"
                value={filtroHasta}
                onChange={(e) => { setFiltroHasta(e.target.value); setLoading(true) }}
                className="bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white/70"
              />
            </div>
          )}
        </div>

        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="kinetic-glass rounded-2xl p-6 animate-pulse">
                  <div className="h-3 w-24 bg-white/10 rounded mb-3" />
                  <div className="h-6 w-16 bg-white/10 rounded" />
                </div>
              ))}
            </div>
            <TableSkeleton rows={5} columns={4} />
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
                <div className="kinetic-glass p-5 rounded-xl flex flex-col">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertCircle className="w-5 h-5 text-rose-400" />
                    <p className="text-sm text-white/60">Alertas Vencidas ({vencidos.length})</p>
                  </div>
                  {vencidos.length === 0 ? (
                    <p className="text-sm text-green-400">No hay miembros vencidos</p>
                  ) : (
                    <div className="max-h-48 overflow-y-auto space-y-1.5">
                      {vencidos.map((v) => (
                        <Link
                          key={v.id}
                          href={`/dashboard/reception?cedula=${v.cedula}`}
                          className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-sm group"
                        >
                          <div className="min-w-0">
                            <p className="text-white font-medium truncate">{v.nombre}</p>
                            <p className="text-white/40 text-xs">{v.cedula}</p>
                          </div>
                          <span className="text-rose-400 font-semibold whitespace-nowrap ml-2">{v.dias_vencido} días vencido</span>
                        </Link>
                      ))}
                    </div>
                  )}
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
                  <tr key={p.id}
                    onClick={async () => {
                      setLoadingDetail(true)
                      try {
                        const config = { headers: { Authorization: `Bearer ${token}` } }
                        const res = await api.get(`/api/v1/admin/payments/${p.id}`, config)
                        setSelectedPayment(res.data)
                      } catch {
                        setError("Error al cargar detalle del pago")
                      } finally {
                        setLoadingDetail(false)
                      }
                    }}
                    className="border-b border-white/4 hover:bg-white/2 transition-all duration-200 cursor-pointer"
                  >
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

      {/* Payment Detail Modal */}
      {(selectedPayment || loadingDetail) && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setSelectedPayment(null)}
        >
          <div
            className="kinetic-glass rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl border border-white/10"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Detalle del Pago #{selectedPayment?.id}</h3>
              <button
                onClick={() => setSelectedPayment(null)}
                className="text-white/40 hover:text-white/80 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {loadingDetail ? (
              <div className="animate-pulse space-y-3">
                {[1,2,3,4,5].map(i => <div key={i} className="h-4 bg-white/10 rounded" style={{width: `${60 + i * 8}%`}} />)}
              </div>
            ) : selectedPayment && (
              <div className="space-y-3 text-sm">
                <div className="border-b border-white/5 pb-2">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Atleta</p>
                  <p className="text-white font-medium">{selectedPayment.miembro_nombre}</p>
                  <p className="text-white/60">{selectedPayment.miembro_cedula}</p>
                </div>
                <div>
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Plan</p>
                  <p className="text-white">{selectedPayment.plan_nombre}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Monto Original</p>
                    <p className="text-white">{Number(selectedPayment.monto_original).toFixed(2)} {selectedPayment.moneda}</p>
                  </div>
                  <div>
                    <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Tasa Cambio</p>
                    <p className="text-white">{Number(selectedPayment.tasa_cambio).toFixed(4)}</p>
                  </div>
                </div>
                <div>
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Monto USD</p>
                  <p className="text-green-400 font-semibold">${Number(selectedPayment.monto_usd).toFixed(2)}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Método de Pago</p>
                    <p className="text-white capitalize">{selectedPayment.metodo_pago.replace(/_/g, " ")}</p>
                  </div>
                  <div>
                    <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Referencia</p>
                    <p className="text-white/70">{selectedPayment.referencia ?? "-"}</p>
                  </div>
                </div>
                <div>
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Fecha</p>
                  <p className="text-white/70">{new Date(selectedPayment.fecha_pago).toLocaleString()}</p>
                </div>
                <div className="border-t border-white/5 pt-2">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Registrado por</p>
                  <p className="text-white">{selectedPayment.registrador_nombre}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}
