'use client';

import { useInfiniteSourceItems } from '@/hooks/api';
import { Navigation } from '@/components/Navigation';
import { RepositoryItem } from '@/components/RepositoryItem';
import { Loading } from '@/components/Loading';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import { ExternalLink, AlertCircle, ArrowLeft, Hash } from 'lucide-react';
import Link from 'next/link';

interface SourceDetailPageProps {
  sourceName: string;
}

export function SourceDetailPage({ sourceName }: SourceDetailPageProps) {
  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteSourceItems(sourceName, 20);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-terminal-bg">
        <Navigation />
        <Loading text={`Loading ${sourceName} items`} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-terminal-bg">
        <Navigation />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="border border-red-500 bg-terminal-bg p-4 sm:p-6 text-center">
            <AlertCircle className="mx-auto mb-4 text-red-500" size={40} />
            <h2 className="text-lg sm:text-xl font-mono mb-2 text-red-500">Source Not Found</h2>
            <p className="text-terminal-gray font-mono text-sm mb-4">
              Unable to load source &ldquo;{sourceName}&rdquo;
            </p>
            <p className="text-xs font-mono text-terminal-gray break-all">
              Error: {error.message}
            </p>
            <Link
              href="/sources"
              className="inline-flex items-center space-x-2 mt-4 px-4 py-2 border border-terminal-border hover:border-terminal-green hover:text-terminal-green transition-colors duration-200 font-mono text-sm"
            >
              <ArrowLeft size={16} />
              <span>Back to Sources</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const allPages = data?.pages ?? [];
  const items = allPages.flatMap(page => page.items);
  const sourceInfo = allPages[0]?.source;
  const hasItems = items.length > 0;

  if (!sourceInfo) {
    return (
      <div className="min-h-screen bg-terminal-bg">
        <Navigation />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="text-center py-12">
            <AlertCircle className="mx-auto mb-4 text-terminal-gray" size={40} />
            <h2 className="text-lg sm:text-xl font-mono mb-2 text-terminal-gray">
              Source Not Found
            </h2>
            <p className="text-terminal-gray font-mono text-sm">
              The source &ldquo;{sourceName}&rdquo; does not exist
            </p>
            <Link
              href="/sources"
              className="inline-flex items-center space-x-2 mt-4 px-4 py-2 border border-terminal-border hover:border-terminal-green hover:text-terminal-green transition-colors duration-200 font-mono text-sm"
            >
              <ArrowLeft size={16} />
              <span>Back to Sources</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Breadcrumb */}
        <div className="mb-4 sm:mb-6">
          <Link
            href="/sources"
            className="inline-flex items-center space-x-2 text-terminal-gray hover:text-terminal-green transition-colors duration-200 font-mono text-sm"
          >
            <ArrowLeft size={16} />
            <span>Sources</span>
          </Link>
        </div>

        {/* Source Header */}
        <div className="mb-6 sm:mb-8">
          <div className="border border-terminal-border bg-terminal-bg p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between space-y-4 sm:space-y-0">
              <div className="flex-1 min-w-0">
                <h1 className="text-xl sm:text-2xl font-mono font-bold text-terminal-green mb-2 break-words">
                  {sourceInfo.name}
                </h1>
                <p className="text-terminal-text text-sm sm:text-base mb-4 leading-relaxed break-words">
                  {sourceInfo.description}
                </p>
                
                <div className="flex flex-col sm:flex-row sm:items-center text-xs sm:text-sm text-terminal-gray space-y-2 sm:space-y-0 sm:space-x-4">
                  <div className="flex items-center space-x-1">
                    <Hash size={12} className="flex-shrink-0" />
                    <span>{sourceInfo.item_count} items</span>
                  </div>
                </div>
              </div>
              
              <div className="flex-shrink-0">
                <a
                  href={sourceInfo.source}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 px-4 py-2 border border-terminal-border hover:border-terminal-green hover:text-terminal-green transition-colors duration-200 font-mono text-sm min-h-[44px]"
                >
                  <ExternalLink size={16} />
                  <span className="hidden sm:inline">View on GitHub</span>
                  <span className="sm:hidden">GitHub</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Items List */}
        {!hasItems && !isLoading && (
          <div className="text-center py-8 sm:py-12">
            <AlertCircle className="mx-auto mb-4 text-terminal-gray" size={40} />
            <h2 className="text-lg sm:text-xl font-mono mb-2 text-terminal-gray">
              No Items Found
            </h2>
            <p className="text-terminal-gray font-mono text-sm">
              This source doesn&apos;t have any items yet
            </p>
          </div>
        )}

        {hasItems && (
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          >
            <div className="space-y-3 sm:space-y-4">
              {items.map((item, index) => (
                <RepositoryItem key={`${item.source}-${index}`} item={item} />
              ))}
            </div>
          </InfiniteScroll>
        )}
      </main>
    </div>
  );
}