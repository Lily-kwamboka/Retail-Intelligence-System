"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  LayoutDashboard, 
  Package, 
  AlertTriangle, 
  Lightbulb, 
  BarChart3, 
  Database,
  LogOut,
  ChevronRight
} from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import ModeToggle from "./ModeToggle";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { name: "Branch Analytics", icon: LayoutDashboard, href: "/" },
  { name: "Inventory Systems", icon: Package, href: "/inventory" },
  { name: "Live Alerts", icon: AlertTriangle, href: "/alerts" },
  { name: "AI Recommendations", icon: Lightbulb, href: "/recommendations" },
  { name: "Branch Scorecard", icon: BarChart3, href: "/scorecard" },
  { name: "Data Pipeline", icon: Database, href: "/data-quality" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <div className="flex flex-col h-screen w-72 bg-card border-r border-border shadow-sm transition-all duration-300">
      <div className="flex items-center gap-3 px-8 py-10">
        <div className="w-10 h-10 bg-orange-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-orange-600/20">
          <span className="font-bold text-xl">M</span>
        </div>
        <div>
          <h1 className="font-extrabold text-foreground tracking-tight text-xl">Msingi</h1>
          <p className="text-[10px] font-bold text-orange-600 uppercase tracking-widest">Enterprise Intel</p>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center justify-between px-4 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200",
                isActive 
                  ? "bg-orange-50 dark:bg-orange-600/10 text-orange-700 dark:text-orange-500" 
                  : "text-muted-foreground hover:bg-gray-50 dark:hover:bg-zinc-800 hover:text-foreground"
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon className={cn(
                  "w-5 h-5 transition-colors",
                  isActive ? "text-orange-700 dark:text-orange-500" : "text-gray-400 group-hover:text-foreground"
                )} />
                <span>{item.name}</span>
              </div>
              {isActive && <ChevronRight className="w-4 h-4 text-orange-600" />}
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-border space-y-1">
        <ModeToggle />
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-3.5 rounded-2xl text-sm font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout Session</span>
        </button>
      </div>
    </div>
  );
}
