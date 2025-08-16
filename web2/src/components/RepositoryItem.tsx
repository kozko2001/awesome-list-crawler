import { AppItem } from '@/types/api';
import { ExternalLink, Clock, Tag } from 'lucide-react';

interface RepositoryItemProps {
  item: AppItem;
}

export function RepositoryItem({ item }: RepositoryItemProps) {
  const formattedDate = new Date(item.time).toLocaleDateString();
  
  return (
    <div className="border border-terminal-border bg-terminal-bg p-3 sm:p-4 hover:border-terminal-green transition-colors duration-200 touch-manipulation">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <a
              href={item.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-terminal-green hover:glow-text font-mono font-semibold flex items-center space-x-1 group min-h-[44px] py-1 break-words"
            >
              <span className="break-all">{item.name}</span>
              <ExternalLink size={14} className="group-hover:scale-110 transition-transform duration-200 flex-shrink-0" />
            </a>
          </div>
          
          <p className="text-terminal-text text-sm sm:text-base mb-3 leading-relaxed break-words">
            {item.description}
          </p>
          
          <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center text-xs sm:text-sm text-terminal-gray space-y-2 sm:space-y-0 sm:space-x-4">
            <div className="flex items-center space-x-1 min-h-[44px] sm:min-h-[32px]">
              <Tag size={12} className="flex-shrink-0" />
              <span>from </span>
              <a
                href={item.list_source}
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-green hover:glow-text underline hover:no-underline transition-all duration-200 break-words"
              >
                {item.list_name}
              </a>
            </div>
            <div className="flex items-center space-x-1 min-h-[44px] sm:min-h-[32px]">
              <Clock size={12} className="flex-shrink-0" />
              <span>{formattedDate}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}