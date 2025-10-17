import React from "react";

interface EventsStatusBarProps {
  isLoading: boolean;
  searchTerm: string;
  isShowingPastEvents: boolean;
  totalCount: number;
}

const EventsStatusBar: React.FC<EventsStatusBarProps> = ({
  isLoading,
  searchTerm,
  isShowingPastEvents,
  totalCount,
}) => {
  const getStatusText = () => {
    if (isLoading) return "Loading..."; 

    if (searchTerm) {
      return `${totalCount} found events`;
    }

    if (isShowingPastEvents) {
      return `${totalCount} total events`;
    }

    return `${totalCount} upcoming events`;
  };

  return <p className="text-sm">{getStatusText()}</p>;
};

export default EventsStatusBar;
