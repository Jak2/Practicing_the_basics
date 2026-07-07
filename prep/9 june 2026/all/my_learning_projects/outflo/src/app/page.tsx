import { getAllPrompts } from "@/lib/markdown";
import HomeClient from "@/components/HomeClient";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({});

export default function HomePage() {
  const prompts = getAllPrompts();
  const allTags = [...new Set(prompts.flatMap((p) => p.tags))].sort();

  return (
    <div className="max-w-6xl mx-auto py-14">
      {/* Hero */}
      <div className="text-center mb-14">
        <div className="inline-block mb-5">
          <span className="text-[0.75em] font-black uppercase tracking-widest border-2 border-neo-black dark:border-white bg-neo-yellow text-neo-black px-3 py-1 rounded-lg">
            Free AI Prompts
          </span>
        </div>
        <h1 className="text-[2.25em] font-black text-neo-black dark:text-white leading-tight mb-4">
          AI Prompts &amp;{" "}
          <span className="bg-neo-yellow text-neo-black px-2 rounded-lg">
            Workflows
          </span>
        </h1>
        <p className="text-[0.875em] font-medium text-[#666] dark:text-[#999] max-w-md mx-auto leading-relaxed">
          Outcome-driven AI workflows that solve real-world problems. Browse,
          copy, and use instantly.
        </p>
      </div>

      <HomeClient prompts={prompts} allTags={allTags} />
    </div>
  );
}
