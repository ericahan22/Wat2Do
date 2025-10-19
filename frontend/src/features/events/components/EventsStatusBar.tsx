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
      return (
        <>
          <span className="font-bold">{totalCount}</span> found events
        </>
      );
    }

    if (isShowingPastEvents) {
      return (
        <>
          <span className="font-bold">{totalCount}</span> total events
        </>
      );
    }

    return (
      <>
        <span className="font-bold">{totalCount}</span> upcoming events
      </>
    );
  };

  return <p className="text-sm">{getStatusText()}</p>;
};

export default EventsStatusBar;
