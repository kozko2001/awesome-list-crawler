import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

// Health check
export const useHealth = () =>
  useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

// Timeline with infinite scroll (1 hour cache)
export const useInfiniteTimeline = (size: number = 10) =>
  useInfiniteQuery({
    queryKey: ['timeline', size],
    queryFn: ({ pageParam = 1 }) => api.timeline(pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60, // 1 hour (formerly cacheTime)
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
export const useInfiniteSearch = (query: string, size: number = 20, sort: string = 'date') =>
  useInfiniteQuery({
    queryKey: ['search', query, size, sort],
    queryFn: ({ pageParam = 1 }) => api.search(query, pageParam, size, sort),
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

// Regular timeline query (for specific pages, 1 hour cache)
export const useTimeline = (page: number = 1, size: number = 10) =>
  useQuery({
    queryKey: ['timeline', page, size],
    queryFn: () => api.timeline(page, size),
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60, // 1 hour (formerly cacheTime)
  });

// Regular items query (for specific pages)
export const useItems = (page: number = 1, size: number = 20) =>
  useQuery({
    queryKey: ['items', page, size],
    queryFn: () => api.items(page, size),
  });

// Search query (for specific pages)
export const useSearch = (query: string, page: number = 1, size: number = 20, sort: string = 'date') =>
  useQuery({
    queryKey: ['search', query, page, size, sort],
    queryFn: () => api.search(query, page, size, sort),
    enabled: !!query.trim(),
  });

// Sources with infinite scroll
export const useInfiniteSources = (size: number = 20) =>
  useInfiniteQuery({
    queryKey: ['sources', size],
    queryFn: ({ pageParam = 1 }) => api.sources(pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
  });

// Sources query (for specific pages)
export const useSources = (page: number = 1, size: number = 20) =>
  useQuery({
    queryKey: ['sources', page, size],
    queryFn: () => api.sources(page, size),
  });

// Source items with infinite scroll (1 hour cache)
export const useInfiniteSourceItems = (sourceName: string, size: number = 20) =>
  useInfiniteQuery({
    queryKey: ['sourceItems', sourceName, size],
    queryFn: ({ pageParam = 1 }) => api.sourceItems(sourceName, pageParam, size),
    getNextPageParam: (lastPage) => 
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
    enabled: !!sourceName.trim(),
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60, // 1 hour (formerly cacheTime)
  });

// Source items query (for specific pages, 1 hour cache)
export const useSourceItems = (sourceName: string, page: number = 1, size: number = 20) =>
  useQuery({
    queryKey: ['sourceItems', sourceName, page, size],
    queryFn: () => api.sourceItems(sourceName, page, size),
    enabled: !!sourceName.trim(),
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60, // 1 hour (formerly cacheTime)
  });