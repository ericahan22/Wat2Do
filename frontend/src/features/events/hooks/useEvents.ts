import { useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { staticEventsData } from "@/data/staticData";
import { useDocumentTitle } from "@/shared/hooks/useDocumentTitle";
import { API_BASE_URL } from "@/shared/constants/api";
import { getTodayString, formatDtstartToMidnight } from "@/shared/lib/dateUtils";
import { isEventOngoing } from "@/shared/lib/eventUtils";
import { Event } from "@/features/events";

// Format the last updated timestamp into a human-readable format (in local time)
const fetchEvents = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<Event[]> => {
  const searchTerm = queryKey[1] || "";
  const dtstart = queryKey[2] || "";
  const addedAt = queryKey[3] || "";

  const params = new URLSearchParams();

  if (searchTerm) {
    params.append("search", searchTerm);
  }

  if (dtstart) {
    params.append("dtstart", formatDtstartToMidnight(dtstart));
  }

  if (addedAt) {
    params.append("added_at", addedAt);
  }

  const queryString = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_BASE_URL}/api/events/${queryString}`);
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: Event[] = await response.json();
  return data;
};

export function useEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const dtstart = searchParams.get("dtstart") || "";
  const addedAt = searchParams.get("added_at") || "";

  const hasActiveFilters = searchTerm !== "" || dtstart !== "" || addedAt !== "";

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm, dtstart, addedAt],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
  });

  const events = useMemo(() => {
    const rawEvents = hasActiveFilters && data ? data : staticEventsData;
    
    if (dtstart) {
      return rawEvents.filter((event) => {
        return event.dtstart.split('T')[0] >= dtstart;
      });
    }

    const todayStr = getTodayString();
    return rawEvents.filter((event) => {
      const eventDate = event.dtstart.split('T')[0];
      if (eventDate > todayStr) return true;
      if (eventDate === todayStr) {
        return isEventOngoing(event);
      }
      return false;
    });
  }, [hasActiveFilters, data, dtstart]);

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    const isLoadingData = hasActiveFilters ? isLoading : false;

    let title: string;

    if (searchTerm) {
      title = `${events.length} Found Events - Wat2Do`;
    } else if (dtstart) {
      title = `${events.length} Total Events - Wat2Do`;
    } else if (addedAt) {
      title = `${events.length} New Events - Wat2Do`;
    } else {
      title = `${events.length} Upcoming Events - Wat2Do`;
    }

    if (!isLoadingData) {
      previousTitleRef.current = title;
    }

    return previousTitleRef.current;
  }, [events.length, isLoading, searchTerm, hasActiveFilters, dtstart, addedAt]);

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

      if (dtstart && dtstart !== todayStr) {
        nextParams.delete("dtstart");
      } else {
        nextParams.set("dtstart", formatDtstartToMidnight("2025-01-01"));
      }
      return nextParams;
    });
  };

  const handleToggleNewEvents = () => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);

      if (addedAt) {
        nextParams.delete("added_at");
      } else {
        const now = new Date();
        const todayAt7am = new Date();
        todayAt7am.setHours(7, 0, 0, 0);
        
        const cutoffDate = now >= todayAt7am ? todayAt7am : new Date(todayAt7am.getTime() - 24 * 60 * 60 * 1000);
        const isoString = cutoffDate.toISOString();
        nextParams.set("added_at", isoString);
        nextParams.delete("dtstart");
      }
      return nextParams;
    });
  };

  return {
    data: events,
    isLoading,
    error,
    searchTerm,
    dtstart,
    addedAt,
    handleViewChange,
    handleToggleStartDate,
    handleToggleNewEvents,
  };
}
