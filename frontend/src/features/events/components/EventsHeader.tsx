import React from "react";
import { getLastUpdatedText } from "@/features/events/hooks/useEvents";

const EventsHeader: React.FC = () => {
  const lastUpdatedText = getLastUpdatedText();

  return (
    <div className="sm:text-left">
      <h1 className="text-3xl font-bold mb-2">Events</h1>
      <p>
        Events update daily at ~8:30am EST.
        {lastUpdatedText && <span className="ml-1">{lastUpdatedText}</span>}
      </p>
    </div>
  );
};

export default EventsHeader;