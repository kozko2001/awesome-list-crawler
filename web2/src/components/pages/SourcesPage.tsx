'use client';

import { useState } from 'react';
import { useInfiniteSources, useInfiniteSourcesSearch } from '@/hooks/api';
import { useDebounce } from '@/hooks/useDebounce';
import { Navigation } from '@/components/Navigation';
import { Loading } from '@/components/Loading';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import { ExternalLink, AlertCircle, Calendar, Hash, Search, X } from 'lucide-react';
import { SourceInfo } from '@/types/api';
import Link from 'next/link';

interface SourceItemProps {
  source: SourceInfo;
}

function SourceItem({ source }: SourceItemProps) {
  const formattedDate = new Date(source.last_updated).toLocaleDateString();
  
  return (
    <div className="border border-terminal-border bg-terminal-bg p-4 hover:border-terminal-green transition-colors duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <Link
              href={`/sources/${encodeURIComponent(source.name)}`}
              className="text-terminal-green hover:glow-text font-mono font-semibold break-words flex-1 min-w-0"
            >
              {source.name}
            </Link>
            <a
              href={source.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-terminal-green hover:glow-text ml-2 flex-shrink-0 group"
              title="View on GitHub"
            >
              <ExternalLink size={12} className="group-hover:scale-110 transition-transform duration-200" />
            </a>
          </div>
          
          <p className="text-terminal-text text-sm mb-3 leading-relaxed">
            {source.description}
          </p>
          
          <div className="flex flex-wrap items-center text-xs text-terminal-gray space-x-4">
            <div className="flex items-center space-x-1">
              <Hash size={10} />
              <span>{source.item_count} items</span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar size={10} />
              <span>Updated {formattedDate}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SourcesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const debouncedQuery = useDebounce(searchQuery, 300);
  
  // Use search hook when there's a query, otherwise use regular sources hook
  const sourcesQuery = useInfiniteSources(20);
  const searchQuery_ = useInfiniteSourcesSearch(debouncedQuery.trim(), 20, sortBy);
  
  // Choose which query to use based on whether we have a search query
  const hasQuery = debouncedQuery.trim().length > 0;
  const activeQuery = hasQuery ? searchQuery_ : sourcesQuery;
  
  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = activeQuery;

  const allPages = data?.pages ?? [];
  const sources = allPages.flatMap(page => page.sources);
  const hasSources = sources.length > 0;

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-mono font-bold text-terminal-green mb-4">
            Awesome Lists Sources
          </h1>
          <p className="text-terminal-gray font-mono text-sm mb-4">
            All awesome lists ordered by most recent update
          </p>
          
          {/* Search Input */}
          <div className="relative mb-4">
            {!searchQuery && (
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-terminal-gray" />
              </div>
            )}
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearch}
              placeholder="Search awesome lists..."
              className={`terminal-input w-full pr-10 text-sm sm:text-base placeholder:text-terminal-gray min-h-[44px] ${searchQuery ? 'pl-3' : 'pl-10'}`}
            />
            {searchQuery && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-terminal-green"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          
          {/* Sort Options */}
          {hasQuery && hasSources && (
            <div className="mt-3 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <span className="text-sm text-terminal-gray font-mono">Sort by:</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setSortBy('date')}
                  className={`px-3 py-2 text-sm font-mono border transition-colors duration-200 min-h-[44px] flex-1 sm:flex-none ${
                    sortBy === 'date'
                      ? 'border-terminal-green text-terminal-green bg-terminal-green/10'
                      : 'border-terminal-border text-terminal-gray hover:border-terminal-green hover:text-terminal-green'
                  }`}
                >
                  Last Update
                </button>
                <button
                  onClick={() => setSortBy('relevance')}
                  className={`px-3 py-2 text-sm font-mono border transition-colors duration-200 min-h-[44px] flex-1 sm:flex-none ${
                    sortBy === 'relevance'
                      ? 'border-terminal-green text-terminal-green bg-terminal-green/10'
                      : 'border-terminal-border text-terminal-gray hover:border-terminal-green hover:text-terminal-green'
                  }`}
                >
                  Best Match
                </button>
              </div>
            </div>
          )}

          {/* Results info */}
          {hasQuery && (
            <p className="mt-2 text-sm text-terminal-gray font-mono">
              {isLoading 
                ? <>Searching for &ldquo;{debouncedQuery}&rdquo;...</>
                : data?.pages[0]?.total 
                  ? <>Found {data.pages[0].total} awesome lists for &ldquo;{debouncedQuery}&rdquo; (sorted by {sortBy === 'date' ? 'last update' : 'best match'})</>
                  : <>No awesome lists found for &ldquo;{debouncedQuery}&rdquo;</>
              }
            </p>
          )}
          
          {!hasQuery && data?.pages[0]?.total && (
            <p className="text-sm text-terminal-gray font-mono">
              Found {data.pages[0].total} awesome lists
            </p>
          )}
        </div>

        {error && (
          <div className="border border-red-500 bg-terminal-bg p-6 text-center mb-8">
            <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
            <h2 className="text-xl font-mono mb-2 text-red-500">Failed to Load Sources</h2>
            <p className="text-terminal-gray font-mono text-sm mb-4">
              Unable to fetch sources
            </p>
            <p className="text-xs font-mono text-terminal-gray">
              Error: {error.message}
            </p>
          </div>
        )}

        {isLoading && (
          <Loading text="Loading awesome lists..." />
        )}

        {!isLoading && hasSources && (
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          >
            <div className="space-y-4">
              {sources.map((source, index) => (
                <SourceItem key={`${source.source}-${index}`} source={source} />
              ))}
            </div>
          </InfiniteScroll>
        )}

        {!isLoading && !hasSources && !error && (
          <div className="text-center py-12">
            {hasQuery ? (
              <>
                <Search className="mx-auto mb-4 text-terminal-gray" size={48} />
                <h2 className="text-xl font-mono mb-2 text-terminal-gray">
                  No sources found
                </h2>
                <p className="text-terminal-gray font-mono text-sm">
                  No awesome lists match &ldquo;{debouncedQuery}&rdquo;
                </p>
                <button
                  onClick={clearSearch}
                  className="mt-4 px-4 py-2 text-sm font-mono border border-terminal-border text-terminal-gray hover:border-terminal-green hover:text-terminal-green transition-colors duration-200"
                >
                  Clear search
                </button>
              </>
            ) : (
              <>
                <AlertCircle className="mx-auto mb-4 text-terminal-gray" size={48} />
                <h2 className="text-xl font-mono mb-2 text-terminal-gray">
                  No sources found
                </h2>
                <p className="text-terminal-gray font-mono text-sm">
                  Unable to load awesome lists
                </p>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}