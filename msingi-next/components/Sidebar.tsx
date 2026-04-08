"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useApi } from "@/hooks/useApi";
import { useState, useEffect } from "react";
import styles from "./Sidebar.module.css";
import ModeToggle from "./ui/ModeToggle";

const NAV = [
  { href: "/dashboard",                  label: "Overview",        icon: "◈" },
  { href: "/dashboard/branches",         label: "Branch Analytics",icon: "⬡" },
  { href: "/dashboard/departments",      label: "Departments",     icon: "⊞" },
  { href: "/dashboard/products",         label: "Products",        icon: "▤" },
  { href: "/dashboard/alerts",           label: "Alerts",          icon: "◉" },
  { href: "/dashboard/recommendations",  label: "Recommendations", icon: "✦" },
  { href: "/dashboard/scorecard",        label: "Scorecard",       icon: "◎" },
  { href: "/dashboard/data-quality",     label: "Data Quality",    icon: "◫" },
];

function parseJwt(token: string) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch { return null; }
}

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout, token } = useAuth();
  const { data: health } = useApi<{ status: string }>("/health");
  const [tokenExpiry, setTokenExpiry] = useState<string>("");
  const [testAlertSent, setTestAlertSent] = useState(false);
  // ✅ NEW: mobile menu open/close state
  const [mobileOpen, setMobileOpen] = useState(false);

  // ✅ NEW: close sidebar when navigating on mobile
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!token) return;
    const payload = parseJwt(token);
    if (!payload?.exp) return;
    const update = () => {
      const diff = payload.exp * 1000 - Date.now();
      if (diff <= 0) { setTokenExpiry("Expired"); return; }
      const m = Math.floor(diff / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      setTokenExpiry(`${m}m ${s}s`);
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [token]);

  const handleTestAlert = () => {
    setTestAlertSent(true);
    setTimeout(() => setTestAlertSent(false), 3000);
    if (token) {
      fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"}/alerts/test`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});
    }
  };

  const connected = health?.status === "ok" || health?.status === "healthy";

  return (
    <>
      {/* ✅ NEW: Hamburger button — only visible on mobile */}
      <button
        className={styles.hamburger}
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle menu"
      >
        {mobileOpen ? "✕" : "☰"}
      </button>

      {/* ✅ NEW: Dark overlay when mobile menu is open */}
      {mobileOpen && (
        <div
          className={styles.overlay}
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`${styles.sidebar} ${mobileOpen ? styles.sidebarOpen : ""}`}>
        <div className={styles.brand}>
          <span className={styles.brandIcon}>✦</span>
          <div>
            <span className={styles.brandName}>Msingi</span>
            <span className={styles.brandSub}>Retail Intelligence</span>
          </div>
        </div>

        <div className={styles.connStatus}>
          <span className={connected ? styles.dotGreen : styles.dotRed} />
          <span className={styles.connLabel}>
            {health === null ? "Connecting…" : connected ? "API Connected" : "API Offline"}
          </span>
        </div>

        <nav className={styles.nav}>
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${active ? styles.active : ""}`}
              >
                <span className={styles.navIcon}>{item.icon}</span>
                <span className={styles.navLabel}>{item.label}</span>
                {active && <span className={styles.activePip} />}
              </Link>
            );
          })}
        </nav>

        <div className={styles.bottom}>
          {tokenExpiry && (
            <div className={styles.tokenExpiry}>
              <span className={styles.tokenIcon}>⏱</span>
              <span>Session: <strong>{tokenExpiry}</strong></span>
            </div>
          )}
          <button
            className={styles.testAlertBtn}
            onClick={handleTestAlert}
            disabled={testAlertSent}
          >
            {testAlertSent ? "✓ Alert Sent!" : "🔔 Test Alert"}
          </button>
          <div className={styles.userInfo}>
            <div className={styles.avatar}>
              {user?.email?.[0]?.toUpperCase() ?? "U"}
            </div>
            <div className={styles.userDetails}>
              <span className={styles.userEmail}>{user?.email}</span>
              <span className={styles.userRole}>{user?.role ?? "viewer"}</span>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={logout}>⏻ Logout</button>
          <ModeToggle />
        </div>
      </aside>
    </>
  );
}
