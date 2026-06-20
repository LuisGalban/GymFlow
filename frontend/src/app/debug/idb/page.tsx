"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/app/components/DashboardLayout";
import { addPendingCheckin, getAllPendingCheckins, clearPendingCheckins } from "@/lib/idb";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

export default function IdbDebugPage() {
  const [pending, setPending] = useState<Array<{ id: number; miembro_id: number; timestamp: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getAllPendingCheckins();
      setPending(data);
    } catch (e: any) {
      setError(e?.message || "Error reading IndexedDB");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleAdd = async () => {
    setLoading(true);
    try {
      await addPendingCheckin(0); // dummy member id
      await refresh();
    } catch (e: any) {
      setError(e?.message || "Error adding check‑in");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    setLoading(true);
    try {
      await clearPendingCheckins();
      await refresh();
    } catch (e: any) {
      setError(e?.message || "Error clearing check‑ins");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout title="🔧 Debug IndexedDB">
      <div className="max-w-2xl mx-auto p-6 kinetic-glass rounded-2xl">
        <h2 className="text-xl font-bold mb-4 text-white">Pending Check‑ins (IndexedDB)</h2>
        {error && (
          <div className="flex items-center gap-2 mb-4 text-rose-400">
            <XCircle className="w-5 h-5" /> {error}
          </div>
        )}
        <button
          onClick={handleAdd}
          disabled={loading}
          className="px-4 py-2 mr-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin inline" /> : "Add dummy check‑in"}
        </button>
        <button
          onClick={handleClear}
          disabled={loading}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded disabled:opacity-50"
        >
          Clear all
        </button>
        <div className="mt-6">
          {loading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <ul className="space-y-2">
              {pending.length === 0 ? (
                <li className="text-gray-400">No pending check‑ins.</li>
              ) : (
                pending.map(p => (
                  <li key={p.id} className="text-white">
                    <CheckCircle2 className="inline w-4 h-4 mr-2" />
                    ID: {p.id}, Miembro: {p.miembro_id}, TS: {p.timestamp}
                  </li>
                ))
              )}
            </ul>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
