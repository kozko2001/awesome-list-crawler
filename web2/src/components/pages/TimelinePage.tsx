'use client';

import { useInfiniteTimeline } from '@/hooks/api';
import { Navigation } from '@/components/Navigation';
import { DayGroup } from '@/components/DayGroup';
import { Loading } from '@/components/Loading';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import { AlertCircle } from 'lucide-react';

export function TimelinePage() {
  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteTimeline(10);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-terminal-bg">
        <Navigation />
        <Loading text="Initializing timeline" />
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
            <h2 className="text-lg sm:text-xl font-mono mb-2 text-red-500">Connection Failed</h2>
            <p className="text-terminal-gray font-mono text-sm mb-4">
              Unable to connect to the backend API
            </p>
            <p className="text-xs font-mono text-terminal-gray break-all">
              Error: {error.message}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const allPages = data?.pages ?? [];
  const timeline = allPages.flatMap(page => page.timeline);

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="mb-6 sm:mb-8">
          <h1 className="text-xl sm:text-2xl font-mono font-bold text-terminal-green mb-2">
            Timeline
          </h1>
          <p className="text-terminal-gray font-mono text-sm sm:text-base">
            Chronological feed of awesome repositories discovered daily
          </p>
        </div>

        {timeline.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-terminal-gray font-mono">
              No data available. The crawler might still be collecting repositories.
            </p>
          </div>
        ) : (
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          >
            <div className="space-y-6 sm:space-y-8">
              {timeline.map((dayData) => (
                <DayGroup key={dayData.date} dayData={dayData} />
              ))}
            </div>
          </InfiniteScroll>
        )}
      </main>
    </div>
  );
}