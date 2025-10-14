import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
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

  const exportToCalendarMutation = useMutation({
    mutationFn: async (eventIds: string[]) => {
      const idsParam = eventIds.join(",");
      const exportUrl = `${API_BASE_URL}/events/export.ics?ids=${idsParam}`;

      // Create a hidden link and trigger download
      // The .ics file is downloaded and can be opened once in Calendar app
      const link = document.createElement("a");
      link.href = exportUrl;
      link.download = "events.ics";
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
  });

  const exportToGoogleCalendarMutation = useMutation({
    mutationFn: async (eventIds: string[]) => {
      const idsParam = eventIds.join(",");
      const response = await fetch(
        `${API_BASE_URL}/events/google-calendar-urls/?ids=${idsParam}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch Google Calendar URLs");
      }

      const data: { urls: string[] } = await response.json();
      return data;
    },
    onSuccess: (data) => {
      data.urls.forEach((url) => {
        window.open(url, "_blank");
      });
    },
  });

  const exportToCalendar = () => {
    const eventIds = Array.from(selectedEvents);
    exportToCalendarMutation.mutate(eventIds);
  };

  const exportToGoogleCalendar = () => {
    const eventIds = Array.from(selectedEvents);
    exportToGoogleCalendarMutation.mutate(eventIds);
  };

  return {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    clearSelection,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
    isExportingToCalendar: exportToCalendarMutation.isPending,
    isExportingToGoogleCalendar: exportToGoogleCalendarMutation.isPending,
    exportError: exportToGoogleCalendarMutation.error,
  };
}
