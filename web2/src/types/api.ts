export interface AppItem {
  name: string;
  description: string;
  source: string;
  list_name: string;
  list_source: string;
  time: string; // ISO date string
}

export interface AppDayData {
  items: AppItem[];
  date: string; // ISO date string
}

export interface TimelineResponse {
  timeline: AppDayData[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export interface ItemsResponse {
  items: AppItem[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export interface HealthResponse {
  status: string;
  data_loaded: boolean;
  total_items: number;
  last_updated: string | null;
}

export interface LuckyResponse {
  timeline: AppDayData[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export interface SourceInfo {
  name: string;
  description: string;
  source: string;
  item_count: number;
  last_updated: string; // ISO date string
}

export interface SourcesResponse {
  sources: SourceInfo[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}