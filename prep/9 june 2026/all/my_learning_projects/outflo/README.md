# Outflo — AI Prompt & Workflow Platform

A production-ready Next.js platform for showcasing AI prompts and workflows. Outflo is a modular, scalable, and SEO-optimized web application that allows users to seamlessly browse, copy, and explore structured prompts and multi-step workflows.

## Features

* **Homepage**: Browse prompt cards with search functionality and tag filtering.
* **Prompt Page**: Dynamic routing using slugs, markdown content rendering, copy-to-clipboard functionality with feedback, and SEO metadata.
* **Workflows Page**: Multi-step rendering where users can easily copy individual workflow steps.
* **Content Management**: Structured content management using Markdown files.
* **UI/UX**: Clean, minimal, and responsive card-based layout with smooth hover effects.
* **Performance**: Optimized with static generation, lazy loading, and clean URLs.
* **Bonus Integrations**: Dark mode support, bookmarking system using local storage, and analytics integration.

## Tech Stack

* **Framework**: Next.js 14 (App Router, SSG)
* **Language**: TypeScript
* **Styling**: Tailwind CSS (Neo-Brutalism design)
* **Content Parsing**: `gray-matter` for frontmatter, `remark` + `remark-html` for Markdown rendering
* **Deployment**: Vercel-ready

## Quick Start

### Prerequisites

Ensure you have Node.js and npm (or your preferred package manager) installed.

### Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd outflo
npm install
```

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application in your browser.

## Project Structure

```text
outflo/
├── content/              ← Markdown content directories
│   ├── prompts/          ← Add .md files here to create prompt pages
│   └── workflows/        ← Add .md files here to create workflow pages
├── src/
│   ├── app/              ← Next.js App Router pages and API routes
│   ├── components/       ← Reusable React components
│   │   ├── cards/        ← PromptCard, WorkflowCard
│   │   ├── layout/       ← Header, Footer
│   │   └── ui/           ← Badge, CopyButton
│   ├── lib/              ← Utility functions
│   │   ├── markdown.ts   ← Content parsing utilities
│   │   └── seo.ts        ← Metadata builder
│   └── types/            ← TypeScript interfaces and types
```

## Adding Content

The platform dynamically reads the `.md` files in the `/content` folders. Adding a new file automatically creates a new card on the UI, adds any new tags to the category filters, and generates a dedicated page.

### New Prompt

Create a new Markdown file at `/content/prompts/my-prompt.md`:

```markdown
---
title: "My Prompt Title"
description: "What this prompt does."
image: ""
tags: ["Tag1", "Tag2"]
created_at: "2024-01-01"
---

Your prompt content here.
```

The prompt will be accessible via the URL slug corresponding to the filename: `/prompts/my-prompt`.

### New Workflow

Create a new Markdown file at `/content/workflows/my-workflow.md`:

```markdown
---
title: "My Workflow"
description: "What this workflow achieves."
image: ""
tags: ["Tag1", "Tag2"]
created_at: "2024-01-01"
---

## Step Title 1

Step content here. This is copyable individually.

## Step Title 2

Next step content here.
```

Each level 2 (`##`) heading in a workflow file becomes a separate, copyable step in the UI.

## Deployment

Outflo is configured for seamless deployment on Vercel:

1. Push your code to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
2. Import the repository in your [Vercel Dashboard](https://vercel.com).
3. Set the `NEXT_PUBLIC_SITE_URL` environment variable to your production URL.
