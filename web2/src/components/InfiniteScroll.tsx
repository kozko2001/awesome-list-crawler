'use client';

import { useEffect } from 'react';
import { useInView } from 'react-intersection-observer';
import { LoadingSpinner } from './Loading';

interface InfiniteScrollProps {
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
  children: React.ReactNode;
}

export function InfiniteScroll({
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  children,
}: InfiniteScrollProps) {
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '200px',
  });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <>
      {children}
      <div ref={ref} className="flex justify-center p-8">
        {isFetchingNextPage && <LoadingSpinner />}
        {!hasNextPage && (
          <div className="text-center text-terminal-gray font-mono text-sm">
            <p>End of transmission.</p>
            <p className="mt-1">$ EOF</p>
          </div>
        )}
      </div>
    </>
  );
}