"use client";

import { useState } from "react";

interface CopyButtonProps {
  text: string;
  label?: string;
  className?: string;
  iconOnly?: boolean;
}

export default function CopyButton({ text, label = "Copy", className = "", iconOnly = false }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (iconOnly) {
    return (
      <button
        onClick={handleCopy}
        aria-label="Copy"
        title="Copy"
        className={`p-1.5 border-2 rounded-xl transition-all ${
          copied
            ? "bg-neo-yellow border-neo-black text-neo-black"
            : "bg-white dark:bg-[#1A1A1A] border-neo-black dark:border-white text-neo-black dark:text-white hover:bg-neo-yellow hover:text-neo-black hover:border-neo-black shadow-neo-sm dark:shadow-neo-white-sm"
        } ${className}`}
      >
        {copied ? (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
          </svg>
        )}
      </button>
    );
  }

  return (
    <button
      onClick={handleCopy}
      className={`inline-flex items-center gap-2 px-4 py-2 text-[0.875em] font-bold border-2 rounded-xl transition-all ${
        copied
          ? "bg-neo-yellow text-neo-black border-neo-black shadow-neo-sm translate-x-0.5 translate-y-0.5"
          : "bg-white dark:bg-[#1A1A1A] text-neo-black dark:text-white border-neo-black dark:border-white shadow-neo dark:shadow-neo-white hover:bg-neo-yellow hover:text-neo-black hover:shadow-neo-sm hover:translate-x-0.5 hover:translate-y-0.5 dark:hover:border-neo-black"
      } ${className}`}
    >
      {copied ? (
        <>
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          Copied!
        </>
      ) : (
        <>
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
          </svg>
          {label}
        </>
      )}
    </button>
  );
}
