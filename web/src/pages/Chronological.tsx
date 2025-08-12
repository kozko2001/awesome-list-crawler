import React from "react";

import "markdown-retro/css/retro.css";
import { useData } from "../data/data";
import DayGroupComponent from "../components/DayGroupComponent";
import LoadingComponent from "../components/LoadingComponent";
import Pagination from "../components/Pagination";
import { useHistory, useLocation } from "react-router-dom";

const INCREMENT = 2;

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function ChonologicalPage() {
  const history = useHistory();
  const query = useQuery();
  const page = query.get("page");
  const search = query.get("search") || "";

  const { data } = useData(search);
  const pageStart = parseInt(page || "0");
  const pageEnd = pageStart + INCREMENT;
  const onPageChange = (pageStart: number, pageEnd: number) => {
    const params = new URLSearchParams();
    params.set("page", pageStart.toString());
    if (search) params.set("search", search);
    history.push(`/?${params.toString()}`);
  };

  const onSearchChange = (searchTerm: string) => {
    const params = new URLSearchParams();
    params.set("page", "0");
    if (searchTerm) params.set("search", searchTerm);
    history.push(`/?${params.toString()}`);
  };

  if (data.timeline.length === 0) {
    return <LoadingComponent />;
  }

  const days = data.timeline
    .slice(pageStart, pageEnd)
    .map((day) => <DayGroupComponent day={day} key={day.date.toISOString()} />);

  const toPrint = data.timeline.length;

  return (
    <div className="App">
      <div style={{ marginBottom: "20px" }}>
        <input
          type="text"
          placeholder="Search items..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{
            padding: "8px 12px",
            fontSize: "16px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            width: "300px",
            maxWidth: "100%"
          }}
        />
      </div>
      found {toPrint} {search && `(filtered by "${search}")`}
      <Pagination
        numItems={data.timeline.length}
        increment={INCREMENT}
        onChange={onPageChange}
        currentPage={pageStart}
      />
      {days}
      <Pagination
        numItems={data.timeline.length}
        increment={INCREMENT}
        onChange={onPageChange}
        currentPage={pageStart}
      />
    </div>
  );
}

export default ChonologicalPage;
