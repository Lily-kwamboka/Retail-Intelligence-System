"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";
import { AlertCircle, Zap, ShieldAlert } from "lucide-react";
import { useRouter } from "next/navigation";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [token, setToken] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    const tk = localStorage.getItem("token");
    if (!tk) {
      router.push("/login");
      return;
    }
    setToken(tk);
    fetchWithAuth("/anomalies", tk).then(data => setAlerts(data || []));
  }, [router]);

  return (
    <div className="max-w-[1400px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="mb-12">
        <h2 className="text-4xl font-extrabold text-foreground tracking-tight">Live Alerts</h2>
        <p className="text-orange-600 font-bold mt-2 uppercase tracking-[0.2em] text-[11px]">Anomalies & Margin Protection System</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
        <div className="bg-card p-8 rounded-[32px] border border-border shadow-sm flex items-center gap-6 transition-colors duration-300">
           <div className="w-16 h-16 bg-orange-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-orange-600/20">
              <Zap className="w-8 h-8" />
           </div>
           <div>
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest leading-loose">Low Margin Events</p>
              <h4 className="text-2xl font-extrabold text-foreground tracking-tight">{alerts.length} Detect</h4>
           </div>
        </div>
      </div>

      <div className="bg-card p-10 rounded-[32px] border border-border shadow-sm transition-colors duration-300">
        <h3 className="text-2xl font-extrabold text-foreground tracking-tight mb-8">System Anomalies</h3>
        <div className="space-y-4">
          {alerts.length > 0 ? alerts.slice(0, 10).map((a, i) => (
            <div key={i} className="flex items-center justify-between p-6 bg-orange-50/10 dark:bg-orange-600/5 border border-orange-100/50 dark:border-orange-900/20 rounded-2xl">
              <div className="flex items-center gap-4">
                 <ShieldAlert className="w-6 h-6 text-orange-600" />
                 <div>
                    <p className="font-extrabold text-foreground">{a.product_name}</p>
                    <p className="text-xs font-semibold text-muted-foreground">{a.branch} • {a.department}</p>
                 </div>
              </div>
              <div className="text-right">
                 <p className="text-orange-600 font-extrabold text-lg">{a.margin_pct}% Margin</p>
                 <p className="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Action Required</p>
              </div>
            </div>
          )) : (
            <div className="py-20 text-center text-muted-foreground italic bg-gray-50/50 dark:bg-zinc-800/30 rounded-[32px] border border-dashed border-border">
               No 10% critical anomalies discovered. System integrity secure.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
