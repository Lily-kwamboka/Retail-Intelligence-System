"use client";

import { useEffect, useState } from "react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";

const COLORS = ["#F97316", "#FB923C", "#FDBA74", "#FED7AA", "#FFEDD5"];

export default function BranchCharts({ data }: { data: { branch: string; total_revenue: number }[] }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // A slight delay ensures the container has had a chance to compute its dimensions
    const timer = setTimeout(() => setMounted(true), 150);
    return () => clearTimeout(timer);
  }, []);

  if (!mounted) return <div className="h-80 w-full bg-card rounded-[32px] animate-pulse border border-border" />;
  
  // Also wait for data to be present if possible, but empty array is handled below

  if (!data || data.length === 0) {
    return (
      <div className="bg-card p-10 rounded-[32px] border border-border shadow-sm">
        <h3 className="text-2xl font-extrabold text-foreground tracking-tight mb-8 text-balance">Branch Revenue Performance</h3>
        <div className="h-80 w-full flex items-center justify-center text-muted-foreground italic">
          No performance data available for current session.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card p-10 rounded-[32px] border border-border shadow-sm transition-colors duration-300 overflow-hidden">
      <h3 className="text-2xl font-extrabold text-foreground tracking-tight mb-8 text-balance">Branch Revenue Performance</h3>
      <div className="w-full">
        {/* Using a fixed height ResponsiveContainer to bypass the -1 calculation error */}
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" opacity={0.1} />
            <XAxis 
              dataKey="branch" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'currentColor', fontSize: 10, fontWeight: 700 }}
              dy={15}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94A3B8', fontSize: 10, fontWeight: 600 }}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(249, 115, 22, 0.05)' }}
              contentStyle={{ 
                borderRadius: "20px", 
                border: "1px solid var(--border)", 
                boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                padding: "16px",
                fontWeight: 800,
                backgroundColor: 'var(--card)',
                color: 'var(--foreground)'
              }}
            />
            <Bar dataKey="total_revenue" radius={[12, 12, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
