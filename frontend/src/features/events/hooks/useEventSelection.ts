import { useState, useEffect } from "react";
import { useApi } from "@/shared/hooks/useApi";

export function useEventSelection(view: "grid" | "calendar") {
  const [isSelectMode, setIsSelectMode] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState<Set<string>>(new Set());
  const { eventsAPIClient } = useApi();

  // Auto-clear selection when switching to calendar view
  useEffect(() => {
    if (view === "calendar") {
      setIsSelectMode(false);
      setSelectedEvents(new Set());
    }
  }, [view]);

  const toggleSelectMode = () => {
    setIsSelectMode(!isSelectMode);
    if (isSelectMode) {
      setSelectedEvents(new Set());
    }
  };

  const clearSelection = () => {
    setIsSelectMode(false);
    setSelectedEvents(new Set());
  };

  const toggleEventSelection = (eventId: string) => {
    setSelectedEvents((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const exportToCalendar = async () => {
    const eventIds = Array.from(selectedEvents).join(",");
    const blob = await eventsAPIClient.exportEventsICS({ ids: eventIds });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "events.ics";
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToGoogleCalendar = async () => {
    const eventIds = Array.from(selectedEvents).join(",");
    const data = await eventsAPIClient.getGoogleCalendarUrls({ ids: eventIds });
    
    data.urls.forEach((url) => {
      window.open(url, "_blank");
    });
  };

  return {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    clearSelection,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
  };
}
