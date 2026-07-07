"use client";

import CopyButton from "@/components/ui/CopyButton";
import type { WorkflowStep } from "@/types";

interface WorkflowStepsProps {
  steps: WorkflowStep[];
}

export default function WorkflowSteps({ steps }: WorkflowStepsProps) {
  return (
    <div className="space-y-5">
      {steps.map((step, index) => (
        <div
          key={index}
          className="bg-white dark:bg-[#1A1A1A] border-2 border-neo-black dark:border-white rounded-2xl shadow-neo dark:shadow-neo-white overflow-hidden"
        >
          {/* Step header */}
          <div className="flex items-center justify-between px-5 py-3 border-b-2 border-neo-black/10 dark:border-white/10 bg-cream dark:bg-neo-black">
            <div className="flex items-center gap-3">
              <span className="w-7 h-7 flex items-center justify-center bg-neo-yellow border-2 border-neo-black rounded-lg text-neo-black text-[0.75em] font-black">
                {index + 1}
              </span>
              <h3 className="font-black text-[0.875em] text-neo-black dark:text-white">
                {step.title}
              </h3>
            </div>
            <CopyButton text={step.content} label="Copy" />
          </div>

          {/* Step content */}
          <pre className="p-5 text-[0.8125em] text-[#444] dark:text-[#CCC] whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto">
            {step.content}
          </pre>
        </div>
      ))}
    </div>
  );
}
