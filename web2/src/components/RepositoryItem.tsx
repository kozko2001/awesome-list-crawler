import { AppItem } from '@/types/api';
import { ExternalLink, Clock, Tag } from 'lucide-react';

interface RepositoryItemProps {
  item: AppItem;
}

export function RepositoryItem({ item }: RepositoryItemProps) {
  const formattedDate = new Date(item.time).toLocaleDateString();
  
  return (
    <div className="border border-terminal-border bg-terminal-bg p-4 hover:border-terminal-green transition-colors duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <a
              href={item.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-terminal-green hover:glow-text font-mono font-semibold flex items-center space-x-1 group"
            >
              <span>{item.name}</span>
              <ExternalLink size={12} className="group-hover:scale-110 transition-transform duration-200" />
            </a>
          </div>
          
          <p className="text-terminal-text text-sm mb-3 leading-relaxed">
            {item.description}
          </p>
          
          <div className="flex flex-wrap items-center text-xs text-terminal-gray space-x-4">
            <div className="flex items-center space-x-1">
              <Tag size={10} />
              <span>from {item.list_name}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock size={10} />
              <span>{formattedDate}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}