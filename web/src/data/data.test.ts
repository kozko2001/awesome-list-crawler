import { convertData } from "./data";

describe("given simple sample data", () => {
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
  it("should convert to timeline", () => {
    const actual = convertData(data);

    expect(actual.timeline).toHaveLength(2);
  });

  it("should be sorted", () => {
    const actual = convertData(data);

    expect(actual.timeline[0].date.getTime()).toBeGreaterThan(
      actual.timeline[1].date.getTime()
    );
  });
});
