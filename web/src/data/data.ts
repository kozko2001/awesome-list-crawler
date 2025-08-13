import React from "react";
import useSWR from "swr";

export interface AppItem {
  name: string;
  description: string;
  source: string;
  list_name: string;
  list_source: string;
  time: Date;
}

export interface AppDayData {
  items: AppItem[];
  date: Date;
}

interface AppData {
  timeline: AppDayData[];
}

interface ApiResponse {
  timeline: AppDayData[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

// API Base URL - will be the same domain with /api/v1 prefix
const API_BASE_URL = "/api/v1";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Transform API response to match existing AppItem interface
const transformApiItem = (item: any): AppItem => ({
  name: item.name,
  description: item.description,
  source: item.source,
  list_name: item.list_name,
  list_source: item.list_source,
  time: new Date(item.time), // API returns ISO string, convert to Date
});

const transformApiResponse = (response: ApiResponse): AppData => {
  const timeline = response.timeline.map((day: any) => ({
    ...day,
    date: new Date(day.date),
    items: day.items.map(transformApiItem),
  }));
  
  return { timeline };
};

const useData = (searchTerm: string = "") => {
  const [debouncedSearchTerm, setDebouncedSearchTerm] = React.useState(searchTerm);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Determine API endpoint based on search term
  const apiUrl = React.useMemo(() => {
    if (!debouncedSearchTerm.trim()) {
      return `${API_BASE_URL}/timeline?page=1&size=50`; // Get more days for initial load
    } else {
      return `${API_BASE_URL}/search?q=${encodeURIComponent(debouncedSearchTerm)}&page=1&size=100`;
    }
  }, [debouncedSearchTerm]);

  const { data: apiResponse, error } = useSWR(apiUrl, fetcher);

  // Transform the response data
  const processedData = React.useMemo(() => {
    if (!apiResponse) return { timeline: [] };

    if (!debouncedSearchTerm.trim()) {
      // For timeline, use the response directly
      return transformApiResponse(apiResponse);
    } else {
      // For search results, we get items instead of timeline
      // Group items by date to create timeline format
      const items = apiResponse.items.map(transformApiItem);
      
      // Group by date
      const groupedByDate: { [key: string]: AppItem[] } = {};
      items.forEach((item) => {
        const dateKey = item.time.toISOString().split('T')[0];
        if (!groupedByDate[dateKey]) {
          groupedByDate[dateKey] = [];
        }
        groupedByDate[dateKey].push(item);
      });

      // Convert to timeline format and sort by date descending
      const timeline: AppDayData[] = Object.entries(groupedByDate)
        .map(([dateStr, items]) => ({
          date: new Date(dateStr),
          items: items.sort((a, b) => b.time.getTime() - a.time.getTime()), // Sort items within day
        }))
        .sort((a, b) => b.date.getTime() - a.date.getTime()); // Sort days descending

      return { timeline };
    }
  }, [apiResponse, debouncedSearchTerm]);

  return {
    data: processedData,
    isLoading: !error && !apiResponse,
    isError: error,
  };
};

const useRandomData = () => {
  const { data: apiResponse, error } = useSWR(
    `${API_BASE_URL}/lucky`,
    fetcher
  );

  const processedData = React.useMemo(() => {
    if (!apiResponse) return { timeline: [] };
    
    return transformApiResponse(apiResponse);
  }, [apiResponse]);

  return {
    data: processedData,
    isLoading: !error && !apiResponse,
    isError: error,
  };
};

// Legacy function for backward compatibility (not used with API)
const convertData = (json?: any): AppData => {
  return { timeline: [] };
};

export { convertData, useData, useRandomData };