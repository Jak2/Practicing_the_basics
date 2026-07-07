import { getAllWorkflows } from "@/lib/markdown";
import { buildMetadata } from "@/lib/seo";
import WorkflowsClient from "@/components/WorkflowsClient";

export const metadata = buildMetadata({
  title: "Workflows",
  description: "Step-by-step AI workflows for marketing, content creation, and business automation.",
  path: "/workflows",
});

export default function WorkflowsPage() {
  const workflows = getAllWorkflows();
  const allTags = [...new Set(workflows.flatMap((w) => w.tags))].sort();

  return (
    <div className="max-w-6xl mx-auto py-14">
      {/* Hero */}
      <div className="text-center mb-14">
        <div className="inline-block mb-5">
          <span className="text-[0.75em] font-black uppercase tracking-widest border-2 border-neo-black dark:border-white bg-neo-black dark:bg-neo-yellow text-white dark:text-neo-black px-3 py-1 rounded-lg">
            Step-by-step
          </span>
        </div>
        <h1 className="text-[2.25em] font-black text-neo-black dark:text-white leading-tight mb-4">
          AI{" "}
          <span className="bg-neo-yellow text-neo-black px-2 rounded-lg">
            Workflows
          </span>
        </h1>
        <p className="text-[0.875em] font-medium text-[#666] dark:text-[#999] max-w-md mx-auto leading-relaxed">
          Multi-step workflows for marketing, content creation, and business
          automation. Copy each step individually.
        </p>
      </div>

      <WorkflowsClient workflows={workflows} allTags={allTags} />
    </div>
  );
}
