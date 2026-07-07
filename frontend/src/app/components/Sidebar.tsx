"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  UserPlus,
  CreditCard,
  BarChart3,
  LogOut,
  Dumbbell,
} from "lucide-react";
import { useAuth } from "@/app/context/AuthContext";

const navItems = [
  { href: "/dashboard/reception", label: "Recepción", icon: LayoutDashboard, roles: ["admin", "worker"] },
  { href: "/members/list", label: "Miembros", icon: Users, roles: ["admin", "worker"] },
  { href: "/members/register", label: "Registrar Atleta", icon: UserPlus, roles: ["admin", "worker"] },
  { href: "/payments/register", label: "Registrar Pago", icon: CreditCard, roles: ["admin", "worker"] },
  { href: "/dashboard/admin", label: "Panel Admin", icon: BarChart3, roles: ["admin"] },
  { href: "/staff/list", label: "Gestionar Personal", icon: Users, roles: ["admin"] },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout, isAdmin } = useAuth();

  const filteredItems = navItems.filter((item) =>
    item.roles.includes(user?.rol || "worker")
  );

  return (
    <aside className="kinetic-glass flex flex-col w-64 min-h-screen shrink-0 px-4 py-6 gap-2">
      {/* Logo */}
      <div className="flex items-center gap-3 px-2 mb-6">
        <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center">
          <Dumbbell className="w-5 h-5 text-indigo-400" />
        </div>
        <div>
          <p className="text-sm font-bold text-white leading-tight">GymFlow</p>
          <p className="text-xs text-white/40 leading-tight">Analytics</p>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex flex-col gap-1 flex-1">
        {filteredItems.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                ${active
                  ? "bg-indigo-500/20 border border-indigo-400/30 text-indigo-300"
                  : "text-white/50 hover:text-white/90 hover:bg-white/5"
                }`}
            >
              <item.icon className="w-4 h-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Usuario y logout */}
      <div className="border-t border-white/8 pt-4 mt-2">
        <div className="flex items-center gap-3 px-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-400/20 flex items-center justify-center text-xs font-bold text-indigo-300">
            {user?.nombre?.charAt(0) ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white/80 truncate">{user?.nombre}</p>
            <p className="text-xs text-white/30">{isAdmin ? "Administrador" : "Recepcionista"}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-xl text-xs text-white/40 hover:text-rose-400 hover:bg-rose-500/10 transition-all duration-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
