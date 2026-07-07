import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getAllWorkflows, getWorkflowBySlug } from "@/lib/markdown";
import { buildMetadata } from "@/lib/seo";
import Badge from "@/components/ui/Badge";
import CopyButton from "@/components/ui/CopyButton";
import WorkflowSteps from "@/components/WorkflowSteps";

interface Props {
  params: { slug: string };
}

export async function generateStaticParams() {
  return getAllWorkflows().map((w) => ({ slug: w.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const workflow = await getWorkflowBySlug(params.slug);
  if (!workflow) return {};
  return buildMetadata({
    title: workflow.title,
    description: workflow.description,
    image: workflow.image,
    path: `/workflows/${workflow.slug}`,
  });
}

export default async function WorkflowPage({ params }: Props) {
  const workflow = await getWorkflowBySlug(params.slug);
  if (!workflow) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: workflow.title,
    description: workflow.description,
    keywords: workflow.tags.join(", "),
    datePublished: workflow.created_at || undefined,
    author: { "@type": "Organization", name: "Outflo" },
    step: workflow.steps.map((s, i) => ({
      "@type": "HowToStep",
      position: i + 1,
      name: s.title,
      text: s.content,
    })),
  };

  const allStepsText =
    workflow.steps.length > 0
      ? workflow.steps
          .map((s, i) => `Step ${i + 1}: ${s.title}\n\n${s.content}`)
          .join("\n\n---\n\n")
      : workflow.rawContent;

  return (
    <div className="max-w-3xl mx-auto py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      {/* Back */}
      <Link
        href="/workflows"
        className="inline-flex items-center gap-2 text-[0.875em] font-bold border-2 border-neo-black dark:border-white bg-white dark:bg-[#1A1A1A] px-4 py-2 rounded-xl shadow-neo dark:shadow-neo-white hover:bg-neo-yellow hover:text-neo-black hover:shadow-neo-sm hover:translate-x-0.5 hover:translate-y-0.5 transition-all mb-10"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </Link>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {workflow.tags.map((tag) => (
          <Badge key={tag} label={tag} />
        ))}
      </div>

      {/* Title */}
      <h1 className="text-[2.25em] font-black text-neo-black dark:text-white mb-3 leading-tight">
        {workflow.title}
      </h1>

      {workflow.description && (
        <p className="text-[0.875em] font-medium text-[#666] dark:text-[#999] mb-8 leading-relaxed">
          {workflow.description}
        </p>
      )}

      {/* Step count + Copy All */}
      <div className="flex items-center justify-between mb-6 p-4 border-2 border-neo-black dark:border-white bg-neo-yellow rounded-2xl shadow-neo dark:shadow-neo-white">
        <span className="text-[0.875em] font-black text-neo-black">
          {workflow.steps.length} step{workflow.steps.length !== 1 ? "s" : ""} in this workflow
        </span>
        <CopyButton text={allStepsText} label="Copy All Steps" />
      </div>

      {workflow.steps.length > 0 ? (
        <WorkflowSteps steps={workflow.steps} />
      ) : (
        <article
          className="prose bg-white dark:bg-[#1A1A1A] border-2 border-neo-black dark:border-white rounded-2xl shadow-neo dark:shadow-neo-white p-6"
          dangerouslySetInnerHTML={{ __html: workflow.content }}
        />
      )}
    </div>
  );
}
