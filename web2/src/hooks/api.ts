import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

// Health check
export const useHealth = () =>
  useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

// Timeline with infinite scroll
export const useInfiniteTimeline = (size: number = 10) =>
  useInfiniteQuery({
    queryKey: ['timeline', size],
    queryFn: ({ pageParam = 1 }) => api.timeline(pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
  });

// Items with infinite scroll
export const useInfiniteItems = (size: number = 20) =>
  useInfiniteQuery({
    queryKey: ['items', size],
    queryFn: ({ pageParam = 1 }) => api.items(pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
  });

// Search with infinite scroll
export const useInfiniteSearch = (query: string, size: number = 20) =>
  useInfiniteQuery({
    queryKey: ['search', query, size],
    queryFn: ({ pageParam = 1 }) => api.search(query, pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
    enabled: !!query.trim(),
  });

// Feeling lucky (random item)
export const useLucky = () =>
  useQuery({
    queryKey: ['lucky'],
    queryFn: api.lucky,
    enabled: false, // Only fetch when explicitly triggered
  });

// Regular timeline query (for specific pages)
export const useTimeline = (page: number = 1, size: number = 10) =>
  useQuery({
    queryKey: ['timeline', page, size],
    queryFn: () => api.timeline(page, size),
  });

// Regular items query (for specific pages)
export const useItems = (page: number = 1, size: number = 20) =>
  useQuery({
    queryKey: ['items', page, size],
    queryFn: () => api.items(page, size),
  });

// Search query (for specific pages)
export const useSearch = (query: string, page: number = 1, size: number = 20) =>
  useQuery({
    queryKey: ['search', query, page, size],
    queryFn: () => api.search(query, page, size),
    enabled: !!query.trim(),
  });