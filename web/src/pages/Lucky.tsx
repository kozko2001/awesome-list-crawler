import React from "react";

import "markdown-retro/css/retro.css";
import { useRandomData } from "../data/data";
import DayGroupComponent from "../components/DayGroupComponent";
import LoadingComponent from "../components/LoadingComponent";

function ChonologicalPage() {
  const { data } = useRandomData();

  if (data.timeline.length === 0) {
    return <LoadingComponent />;
  }

  const days = data.timeline.map((day) => (
    <DayGroupComponent day={day} key={day.date.toISOString()} />
  ));

  const toPrint = data.timeline.length;

  return (
    <div className="App">
      found {toPrint}
      {days}
    </div>
  );
}

export default ChonologicalPage;
