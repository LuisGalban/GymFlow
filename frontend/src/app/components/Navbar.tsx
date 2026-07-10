"use client";
import { useEffect, useState } from "react";
import { Wifi, WifiOff, Clock } from "lucide-react";

export default function Navbar({ title }: { title?: string }) {
  const [isOnline, setIsOnline] = useState(true);
  const [time, setTime] = useState("");

  useEffect(() => {
    setIsOnline(navigator.onLine);
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    const tick = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("es-VE", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    tick();
    const timer = setInterval(tick, 1000);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      clearInterval(timer);
    };
  }, []);

  return (
    <header className="kinetic-glass px-6 py-3 flex items-center justify-between border-b border-white/5">
      <h1 className="text-base font-semibold text-white/80">
        {title ?? "GymFlow Analytics"}
      </h1>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-xs text-white/40">
          <Clock className="w-3.5 h-3.5" />
          <span className="font-mono">{time}</span>
        </div>

        <div
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
            isOnline
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-400 animate-pulse"
          }`}
        >
          {isOnline ? (
            <><Wifi className="w-3 h-3" /> En Línea</>
          ) : (
            <><WifiOff className="w-3 h-3" /> Sin Conexión</>
          )}
        </div>
      </div>
    </header>
  );
}
