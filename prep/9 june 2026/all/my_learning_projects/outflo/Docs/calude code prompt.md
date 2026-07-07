You are a senior full-stack engineer and system architect.

Build a production-ready web application using Next.js (App Router) that serves as a platform for showcasing AI prompts and workflows.

---

## CORE OBJECTIVE

Create a modular, scalable, SEO-optimized platform where:

* Users can browse prompts
* Copy prompts easily
* Explore workflows
* View structured content from Markdown files

---

## TECH STACK

* Next.js (App Router)
* Tailwind CSS
* TypeScript
* Markdown parsing using gray-matter and remark
* Deployment-ready for Vercel

---

## ARCHITECTURE REQUIREMENTS

* Modular folder structure
* Separation of concerns
* Reusable components
* Clean and maintainable code
* Follow industry best practices

---

## FOLDER STRUCTURE

/content/prompts/
/content/workflows/
/app/
/components/
/lib/
/utils/

---

## FEATURES

### 1. Homepage

* Display prompt cards
* Search functionality
* Tag filtering

### 2. Prompt Page

* Dynamic routing using slug
* Render markdown content
* Copy-to-clipboard button
* SEO metadata

### 3. Workflows Page

* Multi-step rendering
* Copy individual steps

---

## MARKDOWN STRUCTURE

Each markdown file must include:

---

title: ""
description: ""
image: ""
tags: []
--------

Content goes here.

---

## FUNCTIONAL REQUIREMENTS

* Parse markdown files dynamically
* Generate static pages
* Implement copy-to-clipboard with feedback
* Optimize for SEO (meta tags, structured data)

---

## UI/UX REQUIREMENTS

* Clean, minimal UI
* Responsive design
* Fast loading
* Card-based layout
* Smooth hover effects

---

## SEO REQUIREMENTS

* Dynamic meta tags
* OpenGraph support
* Clean URLs (/prompts/[slug])

---

## CODE QUALITY

* Use TypeScript everywhere
* Add meaningful comments
* Write reusable utility functions
* Avoid code duplication

---

## PERFORMANCE

* Use static generation where possible
* Optimize images
* Lazy load components

---

## BONUS FEATURES

* Dark mode
* Bookmark system (local storage)
* Analytics integration

---

## OUTPUT

* Full working codebase
* Modular components
* Clear instructions to run locally

---

Do not over-engineer but ensure the system is scalable.
