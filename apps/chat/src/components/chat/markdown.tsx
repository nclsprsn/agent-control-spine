"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

const components: Components = {
  p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  em: ({ children }) => <em className="italic text-foreground/80">{children}</em>,
  h1: ({ children }) => <h1 className="text-[1.125rem] font-semibold mb-2 mt-5 first:mt-0 text-foreground">{children}</h1>,
  h2: ({ children }) => <h2 className="text-[1rem] font-semibold mb-2 mt-4 first:mt-0 text-foreground">{children}</h2>,
  h3: ({ children }) => <h3 className="text-[0.9375rem] font-semibold mb-1.5 mt-3 first:mt-0 text-foreground">{children}</h3>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  code: ({ className, children }) => {
    const isBlock = className?.includes("language-");
    if (isBlock) {
      return (
        <code className="block bg-surface border border-border rounded-lg px-4 py-3 my-3 text-[0.8125rem] font-[family-name:var(--font-mono)] overflow-x-auto whitespace-pre text-foreground/80 leading-relaxed">
          {children}
        </code>
      );
    }
    return (
      <code className="bg-surface border border-border rounded px-1.5 py-0.5 text-[0.8125rem] font-[family-name:var(--font-mono)] text-foreground/80">
        {children}
      </code>
    );
  },
  pre: ({ children }) => <pre className="mb-3">{children}</pre>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-border pl-4 my-3 text-foreground/60 italic">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} className="text-foreground underline underline-offset-2 decoration-muted/40 hover:decoration-foreground transition-colors" target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-3">
      <table className="text-[0.8125rem] border border-border rounded-lg w-full">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-border px-3 py-2 bg-surface font-medium text-left text-foreground/80">{children}</th>,
  td: ({ children }) => <td className="border border-border px-3 py-2 text-foreground/70">{children}</td>,
  hr: () => <hr className="border-border my-4" />,
};

export function Markdown({ content }: { content: string }) {
  return (
    <div className="leading-relaxed">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
