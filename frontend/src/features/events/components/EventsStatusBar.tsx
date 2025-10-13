import React from "react";

interface EventsStatusBarProps {
  isLoading: boolean;
  searchTerm: string;
  isShowingPastEvents: boolean;
  paginatedCount: number;
  totalCount: number;
  view: "grid" | "calendar";
}

const EventsStatusBar: React.FC<EventsStatusBarProps> = ({
  isLoading,
  searchTerm,
  isShowingPastEvents,
  paginatedCount,
  totalCount,
  view,
}) => {
  const getStatusText = () => {
    if (isLoading) return "Loading...";

    // In calendar view, always show total count since pagination doesn't apply
    const displayCount = view === "calendar" ? totalCount : paginatedCount;

    if (searchTerm) {
      return `Showing ${displayCount} of ${totalCount} found events`;
    }

    if (isShowingPastEvents) {
      return `Showing ${displayCount} of ${totalCount} total events`;
    }

    return `Showing ${displayCount} of ${totalCount} upcoming events`;
  };

  return <p className="text-sm">{getStatusText()}</p>;
};

export default EventsStatusBar;
