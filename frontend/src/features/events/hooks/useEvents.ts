import { useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { staticEventsData, LAST_UPDATED } from "@/data/staticData";
import { useDocumentTitle } from "@/shared/hooks/useDocumentTitle";
import { API_BASE_URL } from "@/shared/constants/api";
import { getTodayString } from "@/shared/lib/dateUtils";
import { isEventOngoing } from "@/shared/lib/eventUtils";

export interface Event {
  id: string;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string | null;
  location: string;
  image_url: string | null;
  categories?: string[];
  price: number | null;
  food: string | null;
  registration: boolean;
  club_type?: "WUSA" | "Athletics" | "Student Society" | null;
  added_at: string;
}

// Format the last updated timestamp into a human-readable format (in local time)
export const getLastUpdatedText = (): string => {
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
  return `Last updated on ${dateStr} at ${timeStr}`;
};

const fetchEvents = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<Event[]> => {
  const searchTerm = queryKey[1] || "";
  const startDate = queryKey[2] || "";

  const params = new URLSearchParams();

  if (searchTerm) {
    params.append("search", searchTerm);
  }

  if (startDate) {
    params.append("start_date", startDate);
  }

  const queryString = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_BASE_URL}/events/${queryString}`);
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: Event[] = await response.json();
  return data;
};

export function useEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const startDate = searchParams.get("start_date") || "";

  const hasActiveFilters = searchTerm !== "" || startDate !== "";

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm, startDate],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
  });

  const events = useMemo(() => {
    // When we have active filters but no data yet (loading), keep showing the previous results
    // This prevents the flickering from old results → empty → new results
    if (hasActiveFilters && !data && isLoading) {
      // Return static data filtered by current filters to show something while loading
      const rawEvents = staticEventsData;
      
      if (startDate) {
        return rawEvents.filter((event: Event) => event.date >= startDate);
      }

      const todayStr = getTodayString();
      return rawEvents.filter((event: Event) => {
        if (event.date > todayStr) return true;
        if (event.date === todayStr) {
          return isEventOngoing(event);
        }
        return false;
      });
    }

    const rawEvents = hasActiveFilters && data ? data : staticEventsData;

    if (startDate) {
      return rawEvents.filter((event: Event) => event.date >= startDate);
    }

    const todayStr = getTodayString();
    return rawEvents.filter((event: Event) => {
      if (event.date > todayStr) return true;
      if (event.date === todayStr) {
        return isEventOngoing(event);
      }
      return false;
    });
  }, [hasActiveFilters, data, startDate, isLoading]);

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    const isLoadingData = hasActiveFilters ? isLoading : false;

    let title: string;

    if (searchTerm) {
      title = `${events.length} Found Events - Wat2Do`;
    } else if (startDate) {
      title = `${events.length} Total Events - Wat2Do`;
    } else {
      title = `${events.length} Upcoming Events - Wat2Do`;
    }

    if (!isLoadingData) {
      previousTitleRef.current = title;
    }

    return previousTitleRef.current;
  }, [events.length, isLoading, searchTerm, hasActiveFilters, startDate]);

  useDocumentTitle(documentTitle);

  const handleViewChange = (newView: string) => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.set("view", newView);
      return nextParams;
    });
  };

  const handleToggleStartDate = () => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);

      const todayStr = getTodayString();

      if (startDate && startDate !== todayStr) {
        // Remove start_date to show upcoming events
        nextParams.delete("start_date");
      } else {
        // Set start_date to 2025-01-01 to show past events
        nextParams.set("start_date", "2025-01-01");
      }
      return nextParams;
    });
  };

  return {
    data: events,
    isLoading,
    error,
    searchTerm,
    startDate,
    handleViewChange,
    handleToggleStartDate,
  };
}
