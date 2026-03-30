import React from 'react';
import { ExternalLink, Newspaper, Tag } from 'lucide-react';
import type { NewsArticle } from '../types/stock';

interface NewsCardProps {
  article: NewsArticle;
  compact?: boolean;
}

export const NewsCard: React.FC<NewsCardProps> = ({ article, compact = false }) => {
  const publishedAt = new Date(article.published_at);
  const publishedLabel = Number.isNaN(publishedAt.getTime())
    ? article.published_at
    : publishedAt.toLocaleString();

  return (
    <article className="glass-panel h-full p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-brand-accent dark:bg-brand-accent/10 dark:text-brand-accent">
          <Newspaper className="h-3.5 w-3.5" />
          <span>{article.source}</span>
        </div>
        <span className="text-[11px] text-gray-500 dark:text-gray-400">{publishedLabel}</span>
      </div>

      <h3 className={`${compact ? 'text-sm' : 'text-base'} font-semibold leading-snug text-gray-900 dark:text-white`}>
        {article.title}
      </h3>

      {article.description && !compact && (
        <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-gray-300">{article.description}</p>
      )}

      {article.tickers.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {article.tickers.slice(0, 3).map((ticker) => (
            <span
              key={`${article.url}-${ticker}`}
              className="inline-flex items-center gap-1 rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-[11px] font-semibold text-gray-600 dark:border-gray-700 dark:bg-brand-surfaceHover dark:text-gray-300"
            >
              <Tag className="h-3 w-3" />
              {ticker}
            </span>
          ))}
        </div>
      )}

      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-brand-accent hover:underline"
      >
        Read article
        <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </article>
  );
};
