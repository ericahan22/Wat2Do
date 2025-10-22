import React from "react";
import { LAST_UPDATED } from "@/data/staticData";

const EventsHeader: React.FC = () => {
  const lastUpdatedText = (): string => {
    const date = new Date(LAST_UPDATED);
    const dateStr = date.toLocaleDateString(undefined, {
      month: "long",
      day: "numeric",
    });
    const timeStr = date.toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
    return `Updated ${dateStr} at ${timeStr}`;
  };

  return (
    <div className="sm:text-left">
      <h1 className="text-3xl font-bold mb-2">Events</h1>
      <p>
        Find all the latest club events at UW.
        <span className="ml-1">{lastUpdatedText()}</span>
      </p>
    </div>
  );
};

export default EventsHeader;
