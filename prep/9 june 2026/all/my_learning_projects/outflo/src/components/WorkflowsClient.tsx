"use client";

import { useState, useMemo } from "react";
import WorkflowCard from "@/components/cards/WorkflowCard";
import Badge from "@/components/ui/Badge";
import type { WorkflowMeta } from "@/types";

interface WorkflowsClientProps {
  workflows: WorkflowMeta[];
  allTags: string[];
}

export default function WorkflowsClient({ workflows, allTags }: WorkflowsClientProps) {
  const [search, setSearch] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return workflows.filter((w) => {
      const q = search.toLowerCase();
      const matchSearch =
        q === "" ||
        w.title.toLowerCase().includes(q) ||
        w.description.toLowerCase().includes(q) ||
        w.tags.some((t) => t.toLowerCase().includes(q));
      const matchTag = activeTag === null || w.tags.includes(activeTag);
      return matchSearch && matchTag;
    });
  }, [workflows, search, activeTag]);

  return (
    <div>
      {/* Centered search bar — 1/2 screen width */}
      <div className="flex justify-center mb-8">
        <div className="relative w-full sm:w-1/2">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#888] pointer-events-none"
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="search"
            placeholder="Search workflows..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-[0.875em] font-medium bg-white dark:bg-[#1A1A1A] text-neo-black dark:text-white border-2 border-neo-black dark:border-white rounded-xl shadow-neo dark:shadow-neo-white placeholder:text-[#AAA] focus:outline-none focus:shadow-neo-lg dark:focus:shadow-neo-white-lg transition-shadow"
          />
        </div>
      </div>

      {/* Tag filters — centered */}
      {allTags.length > 0 && (
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          <Badge
            label="All"
            active={activeTag === null}
            onClick={() => setActiveTag(null)}
          />
          {allTags.map((tag) => (
            <Badge
              key={tag}
              label={tag}
              active={activeTag === tag}
              onClick={() => setActiveTag(activeTag === tag ? null : tag)}
            />
          ))}
        </div>
      )}

      {/* Results count */}
      <p className="text-[0.75em] font-bold text-[#999] mb-6 uppercase tracking-widest text-center">
        {filtered.length} workflow{filtered.length !== 1 ? "s" : ""}
        {activeTag ? ` · ${activeTag}` : ""}
        {search ? ` · "${search}"` : ""}
      </p>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="border-2 border-neo-black dark:border-white bg-white dark:bg-[#1A1A1A] rounded-2xl p-16 text-center shadow-neo dark:shadow-neo-white">
          <p className="text-[1em] font-black text-neo-black dark:text-white mb-1">No workflows found</p>
          <p className="text-[0.875em] text-[#888]">Try a different search or tag.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((workflow) => (
            <WorkflowCard key={workflow.slug} workflow={workflow} />
          ))}
        </div>
      )}
    </div>
  );
}
