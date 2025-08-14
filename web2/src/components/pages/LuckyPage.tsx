'use client';

import { useLucky } from '@/hooks/api';
import { Navigation } from '@/components/Navigation';
import { DayGroup } from '@/components/DayGroup';
import { Loading } from '@/components/Loading';
import { Shuffle, RefreshCw, AlertCircle } from 'lucide-react';

export function LuckyPage() {
  const { data, error, isLoading, refetch } = useLucky();

  const handleFeelingLucky = () => {
    refetch();
  };

  return (
    <div className="min-h-screen bg-terminal-bg">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Shuffle className="text-terminal-green" size={32} />
            <h1 className="text-2xl font-mono font-bold text-terminal-green">
              I&apos;m Feeling Lucky
            </h1>
          </div>
          <p className="text-terminal-gray font-mono text-sm mb-6">
            Discover a random awesome repository from the collection
          </p>
          
          <button
            onClick={handleFeelingLucky}
            disabled={isLoading}
            className="terminal-button inline-flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw 
              size={16} 
              className={isLoading ? 'animate-spin' : ''} 
            />
            <span>{isLoading ? 'Rolling dice...' : 'Try Your Luck'}</span>
          </button>
        </div>

        {error && (
          <div className="border border-red-500 bg-terminal-bg p-6 text-center mb-8">
            <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
            <h2 className="text-xl font-mono mb-2 text-red-500">Connection Failed</h2>
            <p className="text-terminal-gray font-mono text-sm mb-4">
              Unable to connect to the backend API
            </p>
            <p className="text-xs font-mono text-terminal-gray">
              Error: {error.message}
            </p>
          </div>
        )}

        {isLoading && <Loading text="Searching for luck" />}

        {data && data.timeline && data.timeline.length > 0 && (
          <div className="mt-8">
            <div className="text-center mb-6">
              <p className="text-terminal-green font-mono text-sm">
                ✨ Your lucky discovery ✨
              </p>
            </div>
            <DayGroup dayData={data.timeline[0]} />
          </div>
        )}

        {!isLoading && !error && !data && (
          <div className="text-center py-12">
            <Shuffle className="mx-auto mb-4 text-terminal-gray" size={48} />
            <p className="text-terminal-gray font-mono">
              Click &quot;Try Your Luck&quot; to discover a random repository
            </p>
          </div>
        )}
      </main>
    </div>
  );
}