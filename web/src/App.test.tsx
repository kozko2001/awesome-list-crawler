import React from "react";
import { SWRConfig } from "swr";
import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

beforeEach(() => {
  fetchMock.resetMocks();
});

test("renders learn react link", async () => {
  const data = {
    lists: [
      {
        name: "LIST1",
        source: "",
        description: "",
        items: [
          {
            name: "ITEM1",
            source: "http://item1.com",
            description: "",
            time: "2019-12-23T13:55:40",
          },
          {
            name: "ITEM2",
            source: "http://item2.com",
            description: "",
            time: "2020-01-01T00:00:00",
          },
          {
            name: "ITEM3",
            source: "http://item3.com",
            description: "",
            time: "2020-01-01T03:00:00",
          },
        ],
      },
    ],
  };
  fetchMock.mockOnce(JSON.stringify(data));
  render(
    <SWRConfig value={{ dedupingInterval: 0 }}>
      <App />
    </SWRConfig>
  );

  const count = await waitFor(() => screen.getByText(/found 2/i));
  expect(count).toBeInTheDocument();

  const item1 = await waitFor(() => screen.getByText(/ITEM1/i));
  expect(item1).toBeInTheDocument();
});
