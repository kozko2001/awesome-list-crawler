import React from "react";

interface PaginationProps {
  numItems: number;
  increment: number;
  currentPage: number;
  onChange: (pageStart: number, pageEnd: number) => void;
}

function Pagination({
  numItems,
  increment,
  currentPage,
  onChange,
}: PaginationProps) {
  const onClick = (newPage: number) => {
    onChange(newPage, newPage + increment);
  };

  let prev = <div />;
  let next = <div />;

  if (currentPage > 0) {
    prev = (
      <button onClick={() => onClick(currentPage - increment)}>
        &lt;- prev{" "}
      </button>
    );
  }

  if (currentPage + increment < numItems) {
    next = (
      <button
        onClick={() => onClick(currentPage + increment)}
        style={{ float: "right" }}
      >
        {" "}
        next -&gt;{" "}
      </button>
    );
  }

  return (
    <div style={{ marginTop: "2em" }}>
      {prev}

      {next}
    </div>
  );
}

export default Pagination;
