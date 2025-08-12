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
  const page = useQuery().get("page");

  const { data } = useData();
  const pageStart = parseInt(page || "0");
  const pageEnd = pageStart + INCREMENT;
  const onPageChange = (pageStart: number, pageEnd: number) => {
    history.push(`/?page=${pageStart}`);
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
      found {toPrint}
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
