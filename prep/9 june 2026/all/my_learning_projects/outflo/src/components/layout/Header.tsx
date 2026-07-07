"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import ThemeToggle from "@/components/ThemeToggle";

const NAV_LINKS = [
  { href: "/", label: "Prompts" },
  { href: "/workflows", label: "Workflows" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 sm:top-4 z-50 py-0 sm:py-3 bg-transparent pointer-events-none">
      {/* Desktop pill nav — 6% margin each side, auto-scales */}
      <div className="hidden sm:flex max-w-6xl mx-auto flex justify-center pointer-events-auto px-[6%]">
        <nav className="inline-flex items-center border-2 border-neo-black dark:border-white bg-white dark:bg-[#1A1A1A] rounded-full shadow-neo dark:shadow-neo-white px-3 py-1 gap-2">
          {/* Logo */}
          <Link
            href="/"
            className="text-[1.125em] font-black text-neo-black dark:text-white px-3 py-0.5 rounded-full hover:bg-cream dark:hover:bg-neo-black transition-colors whitespace-nowrap"
          >
            Out<span className="bg-neo-yellow px-0.5 rounded-sm">flo</span>
          </Link>

          {/* 10% gap after logo */}
          <div className="w-[10%] min-w-[4rem]" />

          {/* Nav links */}
          <div className="flex items-center gap-1">
            {NAV_LINKS.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className={`px-4 py-1 rounded-full text-[0.875em] font-bold transition-all whitespace-nowrap ${pathname === href
                  ? "bg-neo-yellow text-neo-black border-2 border-neo-black"
                  : "text-neo-black dark:text-white hover:bg-neo-yellow/60 hover:text-neo-black"
                  }`}
              >
                {label}
              </Link>
            ))}
          </div>

          {/* 10% gap before toggle */}
          <div className="w-[10%] min-w-[4rem]" />

          {/* Theme toggle */}
          <div className="flex-shrink-0 px-1">
            <ThemeToggle />
          </div>
        </nav>
      </div>

      {/* Mobile top bar — logo + theme only, nav handled by BottomNav */}
      <div className="sm:hidden border-b-2 border-neo-black dark:border-white bg-white dark:bg-[#1A1A1A]">
        <div className="flex items-center justify-between px-[6%] py-2">
          <Link
            href="/"
            className="text-[1.5em] font-black text-neo-black dark:text-white"
          >
            Out<span className="bg-neo-yellow px-0.5 rounded-sm">flo</span>
          </Link>
          <ThemeToggle toggleSize="10px" />
        </div>
      </div>
    </header>
  );
}
