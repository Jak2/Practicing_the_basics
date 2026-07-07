"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  {
    href: "/",
    label: "Prompts",
    icon: (
      <svg style={{ width: "1.1em", height: "1.1em" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    href: "/workflows",
    label: "Workflows",
    icon: (
      <svg style={{ width: "1.1em", height: "1.1em" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
  },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-[#1A1A1A] border-t-2 border-neo-black dark:border-white"
      style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
    >
      <div className="flex items-center justify-around px-[6%] py-2">
        {NAV_LINKS.map(({ href, label, icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-0.5 px-6 py-1.5 rounded-xl border-2 transition-all font-bold hover:-translate-x-[2px] hover:-translate-y-[2px] ${
                active
                  ? "bg-neo-yellow text-neo-black border-neo-black shadow-neo-sm dark:shadow-neo-white-sm"
                  : "bg-white dark:bg-[#1A1A1A] text-neo-black dark:text-white border-neo-black dark:border-white shadow-neo-sm dark:shadow-neo-white-sm hover:bg-neo-yellow/30"
              }`}
            >
              {icon}
              <span style={{ fontSize: "0.6em" }} className="uppercase tracking-widest leading-none font-black">
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
