"use client";
import { useApi } from "@/hooks/useApi";
import DataTable from "@/components/DataTable";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid
} from "recharts";
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

export default function DepartmentsPage() {
  const { data: departments, loading, error } = useApi<Record<string, unknown>[]>("/departments");

  const revKey = departments?.[0]
    ? Object.keys(departments[0]).find(k => /revenue|net_sale|net_sales|current_revenue/i.test(k)) ?? null
    : null;

  const marginKey = departments?.[0]
    ? Object.keys(departments[0]).find(k => /margin/i.test(k)) ?? null
    : null;

  const sorted = (departments ?? [])
    .slice()
    .sort((a, b) => {
      const aRev = revKey ? (a[revKey] as number) || 0 : 0;
      const bRev = revKey ? (b[revKey] as number) || 0 : 0;
      return bRev - aRev;
    });

  return (
    <div>
      <h1 className={styles.pageTitle}>Departments</h1>
      <p className={styles.pageSub}>Revenue, margin, and product variety by department</p>

      {loading ? (
        <div className={styles.spinner} />
      ) : error ? (
        <div className={`${styles.alertBox} ${styles.alertFail}`}>
          Error loading departments: {error}
        </div>
      ) : (
        <>
          {/* Summary badges */}
          <div className={styles.metaRow}>
            <div className={styles.metaBadge}>
              <strong>{sorted.length}</strong>
              Departments
            </div>
            <div className={styles.metaBadge}>
              <strong>
                KES {sorted
                  .reduce((s, d) => s + (revKey ? (d[revKey] as number) || 0 : 0), 0)
                  .toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </strong>
              Total Revenue
            </div>
            <div className={styles.metaBadge}>
              <strong>
                {sorted
                  .reduce((s, d) => s + ((d.unique_products as number) || (d.total_products as number) || 0), 0)
                  .toLocaleString()}
              </strong>
              Total SKUs
            </div>
          </div>

          <div className={styles.chartGrid}>
            {/* Revenue by Department */}
            <div className={`card ${styles.chartCard}`}>
              <h3 className={styles.chartTitle}>Revenue by Department</h3>
              <div style={{ overflowX: "auto", width: "100%" }}>
                <div style={{ minWidth: "800px" }}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={sorted} margin={{ top: 8, right: 16, bottom: 52, left: 8 }} barCategoryGap="30%">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, rgba(255,255,255,0.08))" vertical={false} />
                      <XAxis dataKey="department" tick={tickStyle} angle={-30} textAnchor="end" interval={0} axisLine={{ stroke: "var(--border-color, #444)" }} tickLine={false} />
                      <YAxis tick={tickStyle} tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} axisLine={false} tickLine={false} />
                      <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<CustomTooltip formatter={(v: number) => ({ label: "Revenue", value: `KES ${v.toLocaleString()}` })} />} />
                      <Bar dataKey={revKey ?? "total_revenue"} radius={[5,5,0,0]} maxBarSize={48}>
                        {sorted.map((_, i) => (
                          <Cell key={i} fill={BAR_PALETTE[i % BAR_PALETTE.length]} opacity={0.9} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Margin % by Department */}
            <div className={`card ${styles.chartCard}`}>
              <h3 className={styles.chartTitle}>Avg Margin % by Department</h3>
              <div style={{ overflowX: "auto", width: "100%" }}>
                <div style={{ minWidth: "800px" }}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={sorted} margin={{ top: 8, right: 16, bottom: 52, left: 8 }} barCategoryGap="30%">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, rgba(255,255,255,0.08))" vertical={false} />
                      <XAxis dataKey="department" tick={tickStyle} angle={-30} textAnchor="end" interval={0} axisLine={{ stroke: "var(--border-color, #444)" }} tickLine={false} />
                      <YAxis tick={tickStyle} tickFormatter={(v) => `${v}%`} axisLine={false} tickLine={false} />
                      <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<CustomTooltip formatter={(v: number) => ({ label: "Avg Margin", value: `${v}%` })} />} />
                      <Bar dataKey={marginKey ?? "avg_margin"} radius={[5,5,0,0]} maxBarSize={48}>
                        {sorted.map((row, i) => {
                          const val = marginKey ? (row[marginKey] as number) || 0 : 0;
                          const fill = val < 5 ? "#EF4444" : val < 10 ? "#F97316" : BAR_PALETTE[i % BAR_PALETTE.length];
                          return <Cell key={i} fill={fill} opacity={0.9} />;
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* Full table */}
          <div className={`card ${styles.tableCard}`}>
            <h3 className={styles.chartTitle}>Department Performance Details</h3>
            <div style={{ overflowX: "auto", maxHeight: "400px", overflowY: "auto" }}>
              <div style={{ minWidth: "800px" }}>
                <DataTable data={sorted as Record<string, unknown>[]} />
              </div>
            </div>
          </div>
        </>
      )}

      {!loading && sorted.length === 0 && (
        <div className={`${styles.alertBox} ${styles.alertWarn}`} style={{ marginTop: "1rem" }}>
          ⚠ No department data available. Ensure the view <code>vw_department_performance</code> exists and contains data.
        </div>
      )}
    </div>
  );
}

