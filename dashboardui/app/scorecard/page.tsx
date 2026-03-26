"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Award, Target, TrendingUp, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

export default function ScorecardPage() {
  const [scorecard, setScorecard] = useState<any[]>([]);
  const [token, setToken] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    const tk = localStorage.getItem("token");
    if (!tk) {
      router.push("/login");
      return;
    }
    setToken(tk);
    fetchWithAuth("/scorecard", tk).then(data => setScorecard(data || []));
  }, [router]);

  return (
    <div className="max-w-[1400px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="mb-12">
        <h2 className="text-4xl font-extrabold text-foreground tracking-tight">Branch Scorecard</h2>
        <p className="text-orange-600 font-bold mt-2 uppercase tracking-[0.2em] text-[11px]">Composite Performance Ranking & Metrics</p>
      </header>

      <div className="grid grid-cols-1 gap-10">
        <div className="bg-card p-10 rounded-[32px] border border-border shadow-sm overflow-x-auto transition-colors duration-300">
          <table className="w-full text-left">
            <thead>
              <tr className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest border-b border-border">
                <th className="pb-6 px-4">Rank</th>
                <th className="pb-6 px-4">Branch</th>
                <th className="pb-6 px-4 text-right">Revenue</th>
                <th className="pb-6 px-4 text-right">Margin %</th>
                <th className="pb-6 px-4 text-center">Score</th>
              </tr>
            </thead>
            <tbody className="text-sm font-semibold divide-y divide-border">
              {scorecard.length > 0 ? scorecard.map((s, i) => (
                <tr key={i} className="group hover:bg-orange-50/30 dark:hover:bg-orange-600/5 transition-colors">
                  <td className="py-6 px-4 text-muted-foreground">#{s.rank}</td>
                  <td className="py-6 px-4 text-foreground font-extrabold">{s.branch}</td>
                  <td className="py-6 px-4 text-right">KES {s.total_revenue?.toLocaleString() ?? "0"}</td>
                  <td className="py-6 px-4 text-right text-orange-600">{s.avg_margin ?? "0"}%</td>
                  <td className="py-6 px-4 text-center">
                    <span className="px-4 py-2 bg-orange-600 text-white rounded-xl text-xs font-black shadow-lg shadow-orange-600/10">
                      {s.composite_score ?? "0"}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                   <td colSpan={5} className="py-20 text-center text-muted-foreground italic">Calculating regional composite scores...</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
