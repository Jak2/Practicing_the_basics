import { getAllPrompts, getAllWorkflows } from "@/lib/markdown";
import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://outflo.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const prompts = getAllPrompts();
  const workflows = getAllWorkflows();

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: SITE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${SITE_URL}/workflows`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
  ];

  const promptRoutes: MetadataRoute.Sitemap = prompts.map((p) => ({
    url: `${SITE_URL}/prompts/${p.slug}`,
    lastModified: p.created_at ? new Date(p.created_at) : new Date(),
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  const workflowRoutes: MetadataRoute.Sitemap = workflows.map((w) => ({
    url: `${SITE_URL}/workflows/${w.slug}`,
    lastModified: w.created_at ? new Date(w.created_at) : new Date(),
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  return [...staticRoutes, ...promptRoutes, ...workflowRoutes];
}
