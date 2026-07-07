export interface PromptMeta {
  title: string;
  description: string;
  image?: string;
  tags: string[];
  slug: string;
  created_at?: string;
  rawContent: string; // included so cards can render prompt inline
}

export interface Prompt extends PromptMeta {
  content: string;     // HTML rendered content
  rawContent: string;  // Original markdown text for copy
}

export interface WorkflowMeta {
  title: string;
  description: string;
  image?: string;
  tags: string[];
  slug: string;
  created_at?: string;
}

export interface WorkflowStep {
  title: string;
  content: string; // Raw markdown text
}

export interface Workflow extends WorkflowMeta {
  content: string;     // Full HTML rendered content
  rawContent: string;  // Original markdown text
  steps: WorkflowStep[];
}
