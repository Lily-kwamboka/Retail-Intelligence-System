"use client";

import { useState } from "react";
import { loginUser } from "@/lib/api";
import { motion } from "framer-motion";
import { Lock, Mail, ArrowRight, ShieldCheck, Sparkles } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    const token = await loginUser(email, password);
    if (token) {
      localStorage.setItem("token", token);
      window.location.href = "/";
    } else {
      setError("Invalid credentials. Secure access denied.");
    }
    setIsLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center p-6 z-[1000] overflow-hidden font-sans transition-colors duration-500">
      {/* Aesthetic Background Accents */}
      <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-orange-600/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-amber-500/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, type: "spring", damping: 25 }}
        className="w-full max-w-xl bg-card rounded-[48px] shadow-2xl shadow-gray-200/50 dark:shadow-black/50 p-16 border border-border flex flex-col items-center text-center relative z-10 transition-colors duration-300"
      >
        <div className="w-20 h-20 bg-orange-600 rounded-[28px] flex items-center justify-center text-white mb-10 shadow-xl shadow-orange-600/20 rotate-3">
            <ShieldCheck className="w-10 h-10" />
        </div>

        <h1 className="text-4xl font-extrabold text-foreground tracking-tight leading-tight mb-4">Msingi Intelligence</h1>
        <p className="text-lg font-semibold text-muted-foreground mb-12">Secure Access Portal</p>

        <form onSubmit={handleLogin} className="w-full space-y-6">
          <div className="relative group text-left">
            <Mail className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-orange-600 transition-colors" />
            <input
              type="email"
              placeholder="Enterprise Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-50 dark:bg-zinc-800 border-none rounded-[24px] pl-16 pr-8 py-5 font-bold text-gray-900 dark:text-zinc-100 focus:ring-2 focus:ring-orange-600/20 transition-all outline-none"
              required
            />
          </div>

          <div className="relative group text-left">
            <Lock className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-orange-600 transition-colors" />
            <input
              type="password"
              placeholder="Security PIN"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-50 dark:bg-zinc-800 border-none rounded-[24px] pl-16 pr-8 py-5 font-bold text-gray-900 dark:text-zinc-100 focus:ring-2 focus:ring-orange-600/20 transition-all outline-none"
              required
            />
          </div>

          {error && (
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-500 font-bold text-sm bg-red-50 dark:bg-red-950/20 py-3 rounded-2xl"
            >
              {error}
            </motion.p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-5 bg-orange-600 text-white rounded-[24px] font-extrabold text-lg shadow-2xl shadow-orange-600/20 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
          >
            {isLoading ? "Authenticating..." : (
              <>
                Initialize Access
                <ArrowRight className="w-6 h-6" />
              </>
            )}
          </button>
        </form>

        <div className="mt-12 flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-orange-500 rounded-full animate-pulse"></div>
            <span className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-[0.2em]">Encrypted Session Active</span>
        </div>
      </motion.div>
    </div>
  );
}
