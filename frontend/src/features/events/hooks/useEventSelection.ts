import { useState, useEffect } from "react";

import { API_BASE_URL } from "@/shared/constants/api";

export function useEventSelection(view: "grid" | "calendar") {
  const [isSelectMode, setIsSelectMode] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState<Set<string>>(new Set());

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
    const exportUrl = `${API_BASE_URL}/api/events/export.ics?ids=${eventIds}`;

    const link = document.createElement("a");
    link.href = exportUrl;
    link.download = "events.ics";
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportToGoogleCalendar = async () => {
    const eventIds = Array.from(selectedEvents).join(",");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/events/google-calendar-urls/?ids=${eventIds}`
      );

      if (!response.ok) {
        console.error("Failed to fetch Google Calendar URLs");
        return;
      }

      const data: { urls: string[] } = await response.json();

      data.urls.forEach((url) => {
        window.open(url, "_blank");
      });
    } catch (error) {
      console.error("Error exporting to Google Calendar:", error);
    }
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
