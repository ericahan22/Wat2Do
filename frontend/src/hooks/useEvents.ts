import { useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { staticEventsData, LAST_UPDATED } from "@/data/staticData";
import { useDocumentTitle } from "./useDocumentTitle";

export interface Event {
  id: string;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  image_url: string | null;
  categories?: string[];
  price: number | null;
  food: string | null;
  registration: boolean;
  club_type?: "WUSA" | "Athletics" | "Student Society" | null;
  added_at: string;
}

interface EventsResponse {
  event_ids: string[];
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";

// Format the last updated timestamp into a human-readable format
export const getLastUpdatedText = (): string => {
  const timestamp = LAST_UPDATED;

  if (!timestamp) return "";

  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) {
    return "Updated just now";
  } else if (diffMins < 60) {
    return `Updated ${diffMins} minute${diffMins !== 1 ? "s" : ""} ago`;
  } else if (diffHours < 24) {
    return `Updated ${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
  } else if (diffDays === 1) {
    return "Updated yesterday";
  } else if (diffDays < 7) {
    return `Updated ${diffDays} days ago`;
  } else {
    const dateStr = date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
    const timeStr = date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    return `Updated on ${dateStr} at ${timeStr}`;
  }
};

const fetchEvents = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<EventsResponse> => {
  const searchTerm = queryKey[1] || "";

  const params = new URLSearchParams();

  if (searchTerm) {
    params.append("search", searchTerm);
  }

  const queryString = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_BASE_URL}/api/events/${queryString}`);
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: EventsResponse = await response.json();
  return data;
};

export function useEvents(view: "grid" | "calendar") {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";

  const hasActiveFilters = searchTerm !== "";

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
  });

  const events = useMemo(() => {
    let rawEvents: Event[];

    if (hasActiveFilters && data?.event_ids) {
      rawEvents = data.event_ids
        .map((id) => staticEventsData.get(id))
        .filter(Boolean) as Event[];
    } else {
      rawEvents = Array.from(staticEventsData.values());
    }

    const now = new Date();
    const todayStr =
      now.getFullYear() +
      "-" +
      String(now.getMonth() + 1).padStart(2, "0") +
      "-" +
      String(now.getDate()).padStart(2, "0");

    // Filter for future events and events happening today that haven't finished
    return rawEvents.filter((event) => {
      const eventDateStr = event.date;

      // If event is on a future date, include it
      if (eventDateStr > todayStr) {
        return true;
      }

      // If event is today, check if it hasn't finished yet
      if (eventDateStr === todayStr) {
        const [hours, minutes] = event.end_time.split(":").map(Number);
        const eventEndDateTime = new Date();
        eventEndDateTime.setHours(hours, minutes, 0, 0);

        // Include if event hasn't finished yet (current time < event end time)
        return now < eventEndDateTime;
      }

      return false;
    });
  }, [hasActiveFilters, data?.event_ids]);

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    const isLoadingData = hasActiveFilters ? isLoading : false;

    let title: string;

    if (searchTerm) {
      title = `${events.length} Found Events - Wat2Do`;
    } else {
      title = `${events.length} Upcoming Events - Wat2Do`;
    }

    if (!isLoadingData) {
      previousTitleRef.current = title;
    }

    return previousTitleRef.current;
  }, [view, events.length, isLoading, searchTerm, hasActiveFilters]);

  useDocumentTitle(documentTitle);

  const handleViewChange = (newView: string) => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.set("view", newView);
      return nextParams;
    });
  };

  return {
    data: events,
    isLoading: hasActiveFilters ? isLoading : false,
    error: hasActiveFilters ? error : null,
    searchTerm,
    handleViewChange,
  };
}
