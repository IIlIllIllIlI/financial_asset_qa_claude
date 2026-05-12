"use client";

import type { Citation } from "@/types/api";

export function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
      <p className="text-xs text-gray-500 mb-1">引用来源：</p>
      <ul className="space-y-1">
        {citations.map((c, i) => (
          <li key={i} className="text-xs">
            {c.url ? (
              <a
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {c.title || c.url}
              </a>
            ) : (
              <span className="text-gray-600 dark:text-gray-400">
                {c.title}
              </span>
            )}
            <span className="ml-2 text-gray-400">[{c.source_type}]</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
