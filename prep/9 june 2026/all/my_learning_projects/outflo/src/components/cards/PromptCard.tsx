"use client";

import { useState, useEffect } from "react";
import Badge from "@/components/ui/Badge";
import CopyButton from "@/components/ui/CopyButton";
import type { PromptMeta } from "@/types";

interface PromptCardProps {
  prompt: PromptMeta;
  onTagClick?: (tag: string) => void;
}

function getBookmarks(): string[] {
  try {
    return JSON.parse(localStorage.getItem("bookmarks") ?? "[]");
  } catch {
    return [];
  }
}

export default function PromptCard({ prompt, onTagClick }: PromptCardProps) {
  const [bookmarked, setBookmarked] = useState(false);

  // Sync bookmark state from localStorage on mount
  useEffect(() => {
    setBookmarked(getBookmarks().includes(prompt.slug));
  }, [prompt.slug]);

  function toggleBookmark() {
    const current = getBookmarks();
    const updated = bookmarked
      ? current.filter((s) => s !== prompt.slug)
      : [...current, prompt.slug];
    localStorage.setItem("bookmarks", JSON.stringify(updated));
    setBookmarked(!bookmarked);
  }

  return (
    <div className="bg-white dark:bg-[#1A1A1A] border-2 border-neo-black dark:border-white rounded-2xl shadow-neo dark:shadow-neo-white hover:shadow-neo-lg dark:hover:shadow-neo-white-lg hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all duration-150 flex flex-col">

      {/* Card header */}
      <div className="p-5 pb-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-black text-[1em] text-neo-black dark:text-white leading-snug">
            {prompt.title}
          </h3>

          {/* Action buttons: copy + bookmark — smaller icons */}
          <div className="flex items-center gap-1 shrink-0">
            <CopyButton text={prompt.rawContent} iconOnly />
            <button
              onClick={toggleBookmark}
              aria-label={bookmarked ? "Remove bookmark" : "Bookmark"}
              title={bookmarked ? "Bookmarked" : "Bookmark"}
              className={`p-1.5 border-2 rounded-xl transition-all ${
                bookmarked
                  ? "bg-neo-yellow border-neo-black text-neo-black"
                  : "bg-white dark:bg-[#1A1A1A] border-neo-black dark:border-white text-neo-black dark:text-white hover:bg-neo-yellow hover:border-neo-black hover:text-neo-black shadow-neo-sm dark:shadow-neo-white-sm"
              }`}
            >
              <svg className="w-3.5 h-3.5" fill={bookmarked ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
          </div>
        </div>

        {prompt.description && (
          <p className="text-[0.875em] text-[#666] dark:text-[#999] mb-3 leading-relaxed">
            {prompt.description}
          </p>
        )}

        {/* Tags */}
        {prompt.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5" onClick={(e) => e.stopPropagation()}>
            {prompt.tags.map((tag) => (
              <Badge
                key={tag}
                label={tag}
                onClick={onTagClick ? () => onTagClick(tag) : undefined}
              />
            ))}
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="border-t border-neo-black/10 dark:border-white/10 mx-5" />

      {/* Scrollable prompt content */}
      <div className="px-5 py-4 flex-1">
        <div
          className="overflow-y-auto max-h-44 rounded-xl bg-[#FAFAF7] dark:bg-neo-black border border-neo-black/10 dark:border-white/10 p-3"
          style={{ scrollbarWidth: "thin" }}
        >
          <pre className="text-[0.8125em] text-[#444] dark:text-[#CCC] whitespace-pre-wrap font-mono leading-relaxed">
            {prompt.rawContent}
          </pre>
        </div>
      </div>
    </div>
  );
}
