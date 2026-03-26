"use client";

import { motion } from "framer-motion";
import { TrendingUp, Users, Package, Activity } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const CARDS = [
  { 
    title: "Net Revenue", 
    key: "total_net_revenue", 
    icon: TrendingUp, 
    color: "text-orange-600", 
    bg: "bg-orange-600",
    prefix: "KES ",
    trend: "+12.5%"
  },
  { 
    title: "Active Branches", 
    key: "total_branches", 
    icon: Users, 
    color: "text-amber-600", 
    bg: "bg-amber-600" 
  },
  { 
    title: "Product Lines", 
    key: "total_unique_products", 
    icon: Package, 
    color: "text-blue-600", 
    bg: "bg-blue-600" 
  },
  { 
    title: "Data Pipeline", 
    key: "total_rows", 
    icon: Activity, 
    color: "text-purple-600", 
    bg: "bg-purple-600",
    status: "Live"
  },
];

function Card({ card, value }: { card: typeof CARDS[0], value: any }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-card p-8 rounded-[32px] border border-border shadow-sm relative overflow-hidden group transition-colors duration-300"
    >
      <div className="flex items-start justify-between relative z-10">
        <div className={cn("w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-lg", card.bg)}>
          <card.icon className="w-7 h-7" />
        </div>
        {card.trend && (
          <span className="px-3 py-1 bg-orange-50 dark:bg-orange-950/30 text-orange-600 text-[10px] font-bold rounded-full">
            {card.trend}
          </span>
        )}
        {card.status && (
          <span className="px-3 py-1 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 text-[10px] font-bold rounded-full">
             {card.status}
          </span>
        )}
      </div>
      
      <div className="mt-8 relative z-10">
        <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{card.title}</p>
        <h3 className="text-3xl font-black text-foreground mt-2 tracking-tight">
          {card.prefix}{value?.toLocaleString() || "0"}
        </h3>
      </div>

      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-gray-50/50 dark:bg-zinc-800/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500"></div>
    </motion.div>
  );
}

export default function StatsCards({ summary }: { summary: { total_net_revenue: number; total_branches: number; total_unique_products: number; total_rows: number } | null }) {
  if (!summary) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {CARDS.map((card) => (
        <Card key={card.key} card={card} value={(summary as any)[card.key]} />
      ))}
    </div>
  );
}
