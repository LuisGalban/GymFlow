"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/app/components/DashboardLayout";
import { useAuth, api } from "@/app/context/AuthContext";
import { Loader2, AlertCircle, UserPlus, CheckCircle2 } from "lucide-react";
import { z } from "zod";

const staffSchema = z.object({
  cedula: z.string().min(1, "La cédula es requerida"),
  nombre: z.string().min(1, "El nombre es requerido"),
  correo: z.string().email("Correo electrónico inválido"),
  password: z.string().min(6, "La contraseña debe tener al menos 6 caracteres"),
});

type StaffForm = z.infer<typeof staffSchema>;

export default function StaffRegisterPage() {
  const { token, user, isAdmin, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [form, setForm] = useState<StaffForm>({
    cedula: "",
    nombre: "",
    correo: "",
    password: "",
  });
  const [errors, setErrors] = useState<Partial<Record<keyof StaffForm, string>>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!authLoading && (!token || !user || !isAdmin)) {
      router.push("/dashboard/reception");
    }
  }, [token, user, isAdmin, authLoading, router]);

  function handleChange(field: keyof StaffForm, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");

    const result = staffSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof StaffForm, string>> = {};
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof StaffForm;
        if (!fieldErrors[key]) fieldErrors[key] = issue.message;
      }
      setErrors(fieldErrors);
      return;
    }

    setLoading(true);
    try {
      await api.post(
        "/api/v1/users/register",
        { ...form, rol: "worker" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess("Recepcionista registrado exitosamente.");
      setTimeout(() => router.push("/staff/list"), 1000);
    } catch (err: unknown) {
      const msg =
        err instanceof Object && "response" in err
          ? (err as { response: { data: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg || "Error al registrar recepcionista.");
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || !token || !user || !isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <DashboardLayout title="Registrar Recepcionista">
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

          {/* Cédula */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Cédula</label>
            <input
              type="text"
              value={form.cedula}
              onChange={(e) => handleChange("cedula", e.target.value)}
              placeholder="V-25111222"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
            {errors.cedula && <p className="text-xs text-rose-400">{errors.cedula}</p>}
          </div>

          {/* Nombre */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Nombre completo</label>
            <input
              type="text"
              value={form.nombre}
              onChange={(e) => handleChange("nombre", e.target.value)}
              placeholder="Juan Pérez"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
            {errors.nombre && <p className="text-xs text-rose-400">{errors.nombre}</p>}
          </div>

          {/* Correo */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Correo electrónico</label>
            <input
              type="email"
              value={form.correo}
              onChange={(e) => handleChange("correo", e.target.value)}
              placeholder="correo@ejemplo.com"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
            {errors.correo && <p className="text-xs text-rose-400">{errors.correo}</p>}
          </div>

          {/* Contraseña */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-white/50 uppercase">Contraseña</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => handleChange("password", e.target.value)}
              placeholder="Mínimo 6 caracteres"
              className="w-full bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-400/50"
            />
            {errors.password && <p className="text-xs text-rose-400">{errors.password}</p>}
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
              <><UserPlus className="w-4 h-4" /> Registrar Recepcionista</>
            )}
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
