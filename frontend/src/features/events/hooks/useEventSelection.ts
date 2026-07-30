import { useState, useEffect } from "react";
import { useApi } from "@/shared/hooks/useApi";
import type { Event } from "@/features/events/types/events";

export function useEventSelection(view: "grid" | "calendar", events: Event[]) {
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
    const selected = events.filter((event) => selectedEvents.has(event.occurrence_key));
    const blob = await eventsAPIClient.exportEventsICS(selected);

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
    const selected = events.filter((event) => selectedEvents.has(event.occurrence_key));
    const data = eventsAPIClient.getGoogleCalendarUrls(selected);

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
