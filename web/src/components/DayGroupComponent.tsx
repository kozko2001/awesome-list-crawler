import React from "react";

import { AppDayData } from "../data/data";
import ItemComponent from "./ItemComponent";

interface DayGroupComponentProps {
  day: AppDayData;
}

function DayGroupComponent({ day }: DayGroupComponentProps) {
  const items = day.items.map((i) => <ItemComponent key={i.name} item={i} />);
  return (
    <div>
      <h3>{day.date.toLocaleDateString()} </h3>
      {items}
    </div>
  );
}

export default DayGroupComponent;
