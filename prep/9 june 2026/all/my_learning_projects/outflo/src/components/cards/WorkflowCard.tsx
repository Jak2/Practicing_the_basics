import Link from "next/link";
import Badge from "@/components/ui/Badge";
import type { WorkflowMeta } from "@/types";

interface WorkflowCardProps {
  workflow: WorkflowMeta;
}

export default function WorkflowCard({ workflow }: WorkflowCardProps) {
  return (
    <Link
      href={`/workflows/${workflow.slug}`}
      className="group block bg-white dark:bg-[#1A1A1A] border-2 border-neo-black dark:border-white rounded-2xl shadow-neo dark:shadow-neo-white hover:shadow-neo-lg dark:hover:shadow-neo-white-lg hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all duration-150"
    >

      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-black text-[1em] text-neo-black dark:text-white leading-snug group-hover:underline decoration-2 underline-offset-2">
            {workflow.title}
          </h3>
          <span className="shrink-0 text-[0.75em] font-black px-2.5 py-1 border-2 border-neo-black dark:border-white rounded-lg bg-neo-black dark:bg-neo-yellow text-white dark:text-neo-black">
            Workflow
          </span>
        </div>

        {workflow.description && (
          <p className="text-[0.875em] text-[#666] dark:text-[#999] mb-4 leading-relaxed line-clamp-2">
            {workflow.description}
          </p>
        )}

        <div className="flex flex-wrap gap-1.5">
          {workflow.tags.map((tag) => (
            <Badge key={tag} label={tag} />
          ))}
        </div>
      </div>
    </Link>
  );
}
