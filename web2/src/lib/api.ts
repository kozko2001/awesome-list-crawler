import { TimelineResponse, ItemsResponse, HealthResponse, LuckyResponse, SourcesResponse, SourceItemsResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  
  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }
  
  return response.json();
}

export const api = {
  // Health check
  health: () => fetchApi<HealthResponse>('/api/v1/health'),

  // Timeline with pagination
  timeline: (page: number = 1, size: number = 10) =>
    fetchApi<TimelineResponse>(`/api/v1/timeline?page=${page}&size=${size}`),

  // Items with pagination
  items: (page: number = 1, size: number = 20) =>
    fetchApi<ItemsResponse>(`/api/v1/items?page=${page}&size=${size}`),

  // Search items
  search: (query: string, page: number = 1, size: number = 20, sort: string = 'date') =>
    fetchApi<ItemsResponse>(`/api/v1/search?q=${encodeURIComponent(query)}&page=${page}&size=${size}&sort=${sort}`),

  // Random item (I'm feeling lucky)
  lucky: () => fetchApi<LuckyResponse>('/api/v1/lucky'),

  // Sources list
  sources: (page: number = 1, size: number = 20) =>
    fetchApi<SourcesResponse>(`/api/v1/sources?page=${page}&size=${size}`),

  // Search sources
  searchSources: (query: string, page: number = 1, size: number = 20, sort: string = 'date') =>
    fetchApi<SourcesResponse>(`/api/v1/sources/search?q=${encodeURIComponent(query)}&page=${page}&size=${size}&sort=${sort}`),

  // Source items by source name
  sourceItems: (sourceName: string, page: number = 1, size: number = 20) =>
    fetchApi<SourceItemsResponse>(`/api/v1/sources/${encodeURIComponent(sourceName)}/items?page=${page}&size=${size}&sort=time`),
};

export { ApiError };