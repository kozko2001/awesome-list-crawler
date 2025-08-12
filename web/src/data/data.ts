import groupBy from "lodash/groupBy";
import orderBy from "lodash/orderBy";
import useSWR from "swr";

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

const useData = () => {
  const { data, error } = useSWR(
    "http://awesome-crawler.allocsoc.net/data.json",
    fetcher
  );

  return {
    data: convertData(data),
    isLoading: !error && !data,
    isError: error,
  };
};

const useRandomData = () => {
  const { data, error } = useSWR(
    "http://awesome-crawler.allocsoc.net/data.json",
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
