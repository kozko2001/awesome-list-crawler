import React from "react";

import { AppItem } from "../data/data";

interface ItemProps {
  item: AppItem;
}

function ItemComponent({ item }: ItemProps) {
  return (
    <div>
      <li>
        <a href={item.source}>{item.name}</a> - {item.description} (
        <a href={item.list_source}>{item.list_name}</a>){" "}
      </li>
    </div>
  );
}

export default ItemComponent;
