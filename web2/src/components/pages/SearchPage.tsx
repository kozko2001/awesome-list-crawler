'use client';

import { useState } from 'react';
import { useInfiniteSearch } from '@/hooks/api';
import { useDebounce } from '@/hooks/useDebounce';
import { Navigation } from '@/components/Navigation';
import { RepositoryItem } from '@/components/RepositoryItem';
import { Loading } from '@/components/Loading';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import { Search, AlertCircle, X } from 'lucide-react';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const debouncedQuery = useDebounce(query, 300);

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteSearch(debouncedQuery.trim(), 20, sortBy);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const clearSearch = () => {
    setQuery('');
  };

  const allPages = data?.pages ?? [];
  const items = allPages.flatMap(page => page.items);
  const hasResults = items.length > 0;
  const hasQuery = debouncedQuery.trim().length > 0;

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-mono font-bold text-terminal-green mb-4">
            Search
          </h1>
          
          {/* Search Input */}
          <div className="relative">
            {!query && (
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-terminal-gray" />
              </div>
            )}
            <input
              type="text"
              value={query}
              onChange={handleSearch}
              placeholder="Search repositories... (e.g., 'javascript', 'machine learning', 'react')"
              className={`terminal-input w-full pr-10 text-sm placeholder:text-terminal-gray ${query ? 'pl-3' : 'pl-10'}`}
              autoFocus
            />
            {query && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-terminal-green"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          
          {/* Sort Options */}
          {hasQuery && (
            <div className="mt-3 flex items-center gap-4">
              <span className="text-sm text-terminal-gray font-mono">Sort by:</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setSortBy('date')}
                  className={`px-3 py-1 text-sm font-mono border transition-colors duration-200 ${
                    sortBy === 'date'
                      ? 'border-terminal-green text-terminal-green bg-terminal-green/10'
                      : 'border-terminal-border text-terminal-gray hover:border-terminal-green hover:text-terminal-green'
                  }`}
                >
                  Last Update
                </button>
                <button
                  onClick={() => setSortBy('relevance')}
                  className={`px-3 py-1 text-sm font-mono border transition-colors duration-200 ${
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

          {hasQuery && (
            <p className="mt-2 text-sm text-terminal-gray font-mono">
              {isLoading 
                ? `Searching for "${debouncedQuery}"...`
                : data?.pages[0]?.total 
                  ? `Found ${data.pages[0].total} results for "${debouncedQuery}" (sorted by ${sortBy === 'date' ? 'last update' : 'best match'})`
                  : `No results for "${debouncedQuery}"`
              }
            </p>
          )}
        </div>

        {error && (
          <div className="border border-red-500 bg-terminal-bg p-6 text-center mb-8">
            <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
            <h2 className="text-xl font-mono mb-2 text-red-500">Search Failed</h2>
            <p className="text-terminal-gray font-mono text-sm mb-4">
              Unable to perform search
            </p>
            <p className="text-xs font-mono text-terminal-gray">
              Error: {error.message}
            </p>
          </div>
        )}

        {isLoading && hasQuery && (
          <Loading text={`Searching for "${debouncedQuery}"`} />
        )}

        {!hasQuery && !isLoading && (
          <div className="text-center py-12">
            <Search className="mx-auto mb-4 text-terminal-gray" size={48} />
            <h2 className="text-xl font-mono mb-2 text-terminal-gray">
              Start your search
            </h2>
            <p className="text-terminal-gray font-mono text-sm">
              Enter keywords to find awesome repositories
            </p>
            <div className="mt-4 text-xs text-terminal-gray font-mono">
              <p>Try searching for:</p>
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {['javascript', 'python', 'machine learning', 'react', 'docker', 'api'].map((term) => (
                  <button
                    key={term}
                    onClick={() => setQuery(term)}
                    className="px-2 py-1 border border-terminal-border hover:border-terminal-green hover:text-terminal-green transition-colors duration-200"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {hasQuery && hasResults && (
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          >
            <div className="space-y-4">
              {items.map((item, index) => (
                <RepositoryItem key={`${item.source}-${index}`} item={item} />
              ))}
            </div>
          </InfiniteScroll>
        )}

        {hasQuery && !isLoading && !hasResults && !error && (
          <div className="text-center py-12">
            <Search className="mx-auto mb-4 text-terminal-gray" size={48} />
            <h2 className="text-xl font-mono mb-2 text-terminal-gray">
              No results found
            </h2>
            <p className="text-terminal-gray font-mono text-sm">
              Try different keywords or check your spelling
            </p>
          </div>
        )}
      </main>
    </div>
  );
}