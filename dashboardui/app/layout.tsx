"use client";

import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { usePathname } from "next/navigation";
import { ThemeProvider } from "@/components/theme-provider";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${jakarta.variable} font-sans antialiased text-foreground bg-background`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex min-h-screen transition-colors duration-300">
            {!isLoginPage && <Sidebar />}
            <main className={cn("flex-1 h-screen overflow-y-auto", !isLoginPage && "px-12 py-10")}>
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
