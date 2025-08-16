'use client';

import { useInfiniteSources } from '@/hooks/api';
import { Navigation } from '@/components/Navigation';
import { Loading } from '@/components/Loading';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import { ExternalLink, AlertCircle, Calendar, Hash } from 'lucide-react';
import { SourceInfo } from '@/types/api';

interface SourceItemProps {
  source: SourceInfo;
}

function SourceItem({ source }: SourceItemProps) {
  const formattedDate = new Date(source.last_updated).toLocaleDateString();
  
  return (
    <div className="border border-terminal-border bg-terminal-bg p-4 hover:border-terminal-green transition-colors duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <a
              href={source.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-terminal-green hover:glow-text font-mono font-semibold flex items-center space-x-1 group"
            >
              <span>{source.name}</span>
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
  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteSources(20);

  const allPages = data?.pages ?? [];
  const sources = allPages.flatMap(page => page.sources);
  const hasSources = sources.length > 0;

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-mono font-bold text-terminal-green mb-4">
            Awesome Lists Sources
          </h1>
          <p className="text-terminal-gray font-mono text-sm">
            All awesome lists ordered by most recent update
          </p>
          
          {data?.pages[0]?.total && (
            <p className="mt-2 text-sm text-terminal-gray font-mono">
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
            <AlertCircle className="mx-auto mb-4 text-terminal-gray" size={48} />
            <h2 className="text-xl font-mono mb-2 text-terminal-gray">
              No sources found
            </h2>
            <p className="text-terminal-gray font-mono text-sm">
              Unable to load awesome lists
            </p>
          </div>
        )}
      </main>
    </div>
  );
}