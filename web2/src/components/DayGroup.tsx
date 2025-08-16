import { AppDayData } from '@/types/api';
import { RepositoryItem } from './RepositoryItem';
import { Calendar } from 'lucide-react';

interface DayGroupProps {
  dayData: AppDayData;
}

export function DayGroup({ dayData }: DayGroupProps) {
  const formattedDate = new Date(dayData.date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="mb-6 sm:mb-8">
      {/* Date Header */}
      <div className="sticky top-0 bg-terminal-bg border-b border-terminal-green mb-3 sm:mb-4 pb-2 z-10">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2">
          <div className="flex items-center space-x-2">
            <Calendar size={16} className="text-terminal-green flex-shrink-0" />
            <h2 className="text-base sm:text-lg font-mono font-bold text-terminal-green">
              {formattedDate}
            </h2>
          </div>
          <span className="text-xs sm:text-sm text-terminal-gray font-mono ml-6 sm:ml-0">
            ({dayData.items.length} {dayData.items.length === 1 ? 'item' : 'items'})
          </span>
        </div>
      </div>

      {/* Items */}
      <div className="space-y-3 sm:space-y-4">
        {dayData.items.map((item, index) => (
          <RepositoryItem key={`${item.source}-${index}`} item={item} />
        ))}
      </div>
    </div>
  );
}