"use client";
import { useApi } from "@/hooks/useApi";
import DataTable from "@/components/DataTable";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine, CartesianGrid
} from "recharts";
import { useMemo } from "react";
import styles from "../shared.module.css";

const BAR_PALETTE = [
  "#6366F1","#F59E0B","#10B981","#EF4444",
  "#3B82F6","#EC4899","#14B8A6","#F97316",
  "#8B5CF6","#06B6D4","#84CC16","#A78BFA",
];

const tickStyle = { fontSize: 11, fill: "var(--text-secondary, #888)" };

const CustomTooltip = ({ active, payload, label, formatter }: any) => {
  if (!active || !payload?.length) return null;
  const { label: valLabel, value } = formatter(payload[0].value);
  return (
    <div style={{
      background: "var(--card-bg, #1e1e2e)",
      border: "1px solid var(--border-color, #333)",
      borderRadius: 8,
      padding: "10px 14px",
      fontSize: 13,
      color: "var(--text-primary, #f0f0f0)",
      boxShadow: "0 4px 16px rgba(0,0,0,0.25)",
    }}>
      <p style={{ margin: 0, fontWeight: 600, marginBottom: 4 }}>{label}</p>
      <p style={{ margin: 0, color: payload[0].fill }}>{valLabel}: <strong>{value}</strong></p>
    </div>
  );
};

export default function BranchesPage() {
  const { data: branches, loading } = useApi<Record<string,unknown>[]>("/branches");
  const { data: scorecard } = useApi<Record<string,unknown>[]>("/scorecard");

  const display = (branches && branches.length > 0) ? branches : scorecard ?? [];

  const revKey = display[0]
    ? Object.keys(display[0]).find(k => /revenue|net_sale|net_sales|current_revenue/i.test(k)) ?? null
    : null;

  const marginKey = display[0]
    ? Object.keys(display[0]).find(k => /margin/i.test(k)) ?? null
    : null;

  const chartData = useMemo(() => display, [display]);
  const chartWidth = Math.max(600, 80 * chartData.length);

  if (!display.length && !loading) {
    return (
      <div>
        <h1 className={styles.pageTitle}>Branch Analytics</h1>
        <p className={styles.pageSub}>Revenue and margin performance by location</p>
        <div className="alert alert-warning">
          No branch data available. Please check your database and run the analytics views.
        </div>
      </div>
    );
  }

  const revenueKey    = `revenue-${chartData.length}-${revKey}`;
  const marginKeyUniq = `margin-${chartData.length}-${marginKey}`;

  return (
    <div>
      <h1 className={styles.pageTitle}>Branch Analytics</h1>
      <p className={styles.pageSub}>Revenue and margin performance by location</p>

      {loading ? (
        <div className={styles.spinner} />
      ) : (
        <>
          <div className={styles.chartGrid}>
            {revKey && chartData.length > 0 && (
              <div className={`card ${styles.chartCard}`}>
                <h3 className={styles.chartTitle}>Revenue by Branch</h3>
                <div style={{ overflowX: "auto", width: "100%" }}>
                  <div style={{ width: `${chartWidth}px` }}>
                    <ResponsiveContainer key={revenueKey} width="100%" height={300}>
                      <BarChart data={chartData} margin={{ top: 8, right: 16, bottom: 48, left: 8 }} barCategoryGap="30%">
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, rgba(255,255,255,0.08))" vertical={false} />
                        <XAxis dataKey="branch" tick={tickStyle} angle={-30} textAnchor="end" interval={0} axisLine={{ stroke: "var(--border-color, #444)" }} tickLine={false} />
                        <YAxis tick={tickStyle} tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} axisLine={false} tickLine={false} />
                        <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<CustomTooltip formatter={(v: number) => ({ label: "Revenue", value: `KES ${v.toLocaleString()}` })} />} />
                        <Bar dataKey={revKey} radius={[5,5,0,0]} maxBarSize={48}>
                          {chartData.map((_, i) => <Cell key={i} fill={BAR_PALETTE[i % BAR_PALETTE.length]} opacity={0.9} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {marginKey && chartData.length > 0 && (
              <div className={`card ${styles.chartCard}`}>
                <h3 className={styles.chartTitle}>Margin % by Branch</h3>
                <div style={{ overflowX: "auto", width: "100%" }}>
                  <div style={{ width: `${chartWidth}px` }}>
                    <ResponsiveContainer key={marginKeyUniq} width="100%" height={300}>
                      <BarChart data={chartData} margin={{ top: 8, right: 16, bottom: 48, left: 8 }} barCategoryGap="30%">
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, rgba(255,255,255,0.08))" vertical={false} />
                        <XAxis dataKey="branch" tick={tickStyle} angle={-30} textAnchor="end" interval={0} axisLine={{ stroke: "var(--border-color, #444)" }} tickLine={false} />
                        <YAxis tick={tickStyle} tickFormatter={(v) => `${v}%`} axisLine={false} tickLine={false} />
                        <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<CustomTooltip formatter={(v: number) => ({ label: "Avg Margin", value: `${v}%` })} />} />
                        <ReferenceLine y={5} stroke="#EF4444" strokeDasharray="5 4" label={{ value: "5% Min", fill: "#EF4444", fontSize: 11, position: "insideTopRight" }} />
                        <Bar dataKey={marginKey} radius={[5,5,0,0]} maxBarSize={48}>
                          {chartData.map((row, i) => {
                            const val = Number(row[marginKey!] ?? 0);
                            const fill = val < 5 ? "#EF4444" : val < 10 ? "#F97316" : BAR_PALETTE[i % BAR_PALETTE.length];
                            return <Cell key={i} fill={fill} opacity={0.9} />;
                          })}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className={`card ${styles.tableCard}`}>
            <h3 className={styles.chartTitle}>Branch Performance Details</h3>
            <DataTable key={`table-${chartData.length}`} data={chartData} />
          </div>
        </>
      )}
    </div>
  );
}
