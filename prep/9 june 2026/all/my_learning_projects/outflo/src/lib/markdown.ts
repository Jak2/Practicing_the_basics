import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import remarkHtml from "remark-html";
import type { PromptMeta, Prompt, WorkflowMeta, Workflow, WorkflowStep } from "@/types";

const PROMPTS_DIR = path.join(process.cwd(), "content", "prompts");
const WORKFLOWS_DIR = path.join(process.cwd(), "content", "workflows");

// ─── Prompts ──────────────────────────────────────────────────────────────────

export function getAllPrompts(): PromptMeta[] {
  if (!fs.existsSync(PROMPTS_DIR)) return [];
  const files = fs.readdirSync(PROMPTS_DIR).filter((f) => f.endsWith(".md"));

  return files
    .map((filename) => {
      const slug = filename.replace(/\.md$/, "");
      const raw = fs.readFileSync(path.join(PROMPTS_DIR, filename), "utf-8");
      const { data, content } = matter(raw);
      return {
        slug,
        title: data.title ?? slug,
        description: data.description ?? "",
        image: data.image ?? "",
        tags: Array.isArray(data.tags) ? data.tags : [],
        created_at: data.created_at ?? "",
        rawContent: content.trim(),
      } as PromptMeta;
    })
    .sort((a, b) =>
      (b.created_at ?? "") > (a.created_at ?? "") ? 1 : -1
    );
}

export async function getPromptBySlug(slug: string): Promise<Prompt | null> {
  const filepath = path.join(PROMPTS_DIR, `${slug}.md`);
  if (!fs.existsSync(filepath)) return null;

  const raw = fs.readFileSync(filepath, "utf-8");
  const { data, content } = matter(raw);
  const processed = await remark().use(remarkHtml).process(content);

  return {
    slug,
    title: data.title ?? slug,
    description: data.description ?? "",
    image: data.image ?? "",
    tags: Array.isArray(data.tags) ? data.tags : [],
    created_at: data.created_at ?? "",
    content: processed.toString(),
    rawContent: content.trim(),
  };
}

// ─── Workflows ────────────────────────────────────────────────────────────────

export function getAllWorkflows(): WorkflowMeta[] {
  if (!fs.existsSync(WORKFLOWS_DIR)) return [];
  const files = fs.readdirSync(WORKFLOWS_DIR).filter((f) => f.endsWith(".md"));

  return files
    .map((filename) => {
      const slug = filename.replace(/\.md$/, "");
      const raw = fs.readFileSync(path.join(WORKFLOWS_DIR, filename), "utf-8");
      const { data } = matter(raw);
      return {
        slug,
        title: data.title ?? slug,
        description: data.description ?? "",
        image: data.image ?? "",
        tags: Array.isArray(data.tags) ? data.tags : [],
        created_at: data.created_at ?? "",
      } as WorkflowMeta;
    })
    .sort((a, b) =>
      (b.created_at ?? "") > (a.created_at ?? "") ? 1 : -1
    );
}

export async function getWorkflowBySlug(slug: string): Promise<Workflow | null> {
  const filepath = path.join(WORKFLOWS_DIR, `${slug}.md`);
  if (!fs.existsSync(filepath)) return null;

  const raw = fs.readFileSync(filepath, "utf-8");
  const { data, content } = matter(raw);

  const steps = parseWorkflowSteps(content);
  const processed = await remark().use(remarkHtml).process(content);

  return {
    slug,
    title: data.title ?? slug,
    description: data.description ?? "",
    image: data.image ?? "",
    tags: Array.isArray(data.tags) ? data.tags : [],
    created_at: data.created_at ?? "",
    content: processed.toString(),
    rawContent: content.trim(),
    steps,
  };
}

/**
 * Split workflow markdown into steps using ## headings as delimiters.
 * Each H2 section becomes one step with its raw text content.
 */
function parseWorkflowSteps(content: string): WorkflowStep[] {
  const lines = content.split("\n");
  const steps: WorkflowStep[] = [];
  let currentTitle = "";
  let currentLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("## ")) {
      if (currentTitle) {
        steps.push({ title: currentTitle, content: currentLines.join("\n").trim() });
      }
      currentTitle = line.replace(/^## /, "").trim();
      currentLines = [];
    } else {
      currentLines.push(line);
    }
  }

  if (currentTitle) {
    steps.push({ title: currentTitle, content: currentLines.join("\n").trim() });
  }

  return steps;
}
