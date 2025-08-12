import React from "react";
import groupBy from "lodash/groupBy";
import orderBy from "lodash/orderBy";
import useSWR from "swr";
import Fuse from "fuse.js";

interface JSONItem {
  name: string;
  source: string;
  description: string;
  time: string;
}

interface JSONList {
  name: string;
  description: string;
  source: string;
  items: JSONItem[];
}

interface JSONData {
  lists: JSONList[];
}

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

const collectItems = (json: JSONData): AppItem[] => {
  const items = json.lists
    .map((l) =>
      l.items.map((i) => {
        return {
          ...i,
          list_name: l.name,
          list_source: l.source,
          time: new Date(i.time.split("T")[0]),
        };
      })
    )
    .flat();
  return items;
};

const convertData = (json?: JSONData): AppData => {
  if (!json) {
    return { timeline: [] };
  }

  const items = collectItems(json);
  const grouped: AppItem[][] = Object.values(
    groupBy(items, (i: AppItem) => i.time)
  );

  const x: AppDayData[] = grouped.map((g: AppItem[]) => {
    return {
      items: g,
      date: g[0].time,
    };
  });

  return {
    timeline: orderBy(x, (p: AppDayData) => p.date, ["desc"]),
  };
};

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const useData = (searchTerm: string = "") => {
  const { data, error } = useSWR(
    "https://s3.eu-west-1.amazonaws.com/awesome-crawler.allocsoc.net/data.json",
    fetcher
  );

  const [debouncedSearchTerm, setDebouncedSearchTerm] = React.useState(searchTerm);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const fuse = React.useMemo(() => {
    if (!data) return null;

    const items = collectItems(data);
    return new Fuse(items, {
      keys: [
        { name: 'name', weight: 0.4 },
        { name: 'description', weight: 0.3 },
        { name: 'list_name', weight: 0.2 },
        { name: 'source', weight: 0.1 }
      ],
      threshold: 0.3,
      includeScore: true
    });
  }, [data]);

  const processedData = React.useMemo(() => {
    if (!data) return { timeline: [] };

    // If search term is changing (before debounce), show empty results
    if (searchTerm !== debouncedSearchTerm) {
      return { timeline: [] };
    }

    if (!debouncedSearchTerm.trim()) {
      return convertData(data);
    }

    if (!fuse) return { timeline: [] };

    const searchResults = fuse.search(debouncedSearchTerm);
    const filteredItems = searchResults.map(result => result.item);

    const grouped: AppItem[][] = Object.values(
      groupBy(filteredItems, (i: AppItem) => i.time)
    );

    const timeline: AppDayData[] = grouped.map((g: AppItem[]) => ({
      items: g,
      date: g[0].time,
    }));

    return {
      timeline: orderBy(timeline, (p: AppDayData) => p.date, ["desc"]),
    };
  }, [data, searchTerm, debouncedSearchTerm, fuse]);

  return {
    data: processedData,
    isLoading: !error && !data,
    isError: error,
  };
};

const useRandomData = () => {
  const { data, error } = useSWR(
    "https://s3.eu-west-1.amazonaws.com/awesome-crawler.allocsoc.net/data.json",
    fetcher
  );

  let randomData: JSONData;

  if (data) {
    const randomList =
      data.lists[Math.floor(Math.random() * data.lists.length)];

    randomData = {
      lists: [randomList],
    };
  } else {
    randomData = { lists: [] };
  }

  console.log(randomData);
  return {
    data: convertData(randomData),
    isLoading: !error && !data,
    isError: error,
  };
};

export { convertData, useData, useRandomData };
