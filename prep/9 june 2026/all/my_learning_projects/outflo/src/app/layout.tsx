import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import BottomNav from "@/components/layout/BottomNav";
import { buildMetadata } from "@/lib/seo";

const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600", "700", "800", "900"] });

export const metadata: Metadata = buildMetadata({});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>" />
        {/* Prevent dark-mode flash on load */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{const t=localStorage.getItem('theme');if(t==='dark'){document.documentElement.classList.add('dark')}}catch(_){}`,
          }}
        />
      </head>
      <body
        className={`${inter.className} bg-cream dark:bg-neo-black text-neo-black dark:text-white min-h-screen flex flex-col`}
      >
        <Header />
        <main className="flex-1 px-[10%] sm:px-[6%] lg:px-[12%] pb-[5rem] sm:pb-0">{children}</main>
        <Footer className="hidden sm:block" />
        <BottomNav />
      </body>
    </html>
  );
}
