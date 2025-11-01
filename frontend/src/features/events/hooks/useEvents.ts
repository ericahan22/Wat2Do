import { useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useDocumentTitle } from "@/shared/hooks/useDocumentTitle";
import { useApi } from "@/shared/hooks/useApi";
import { getTodayString, formatDtstartToMidnight } from "@/shared/lib/dateUtils";

export function useEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { eventsAPIClient } = useApi();
  const searchTerm = searchParams.get("search") || "";
  const dtstart_utc = searchParams.get("dtstart_utc") || "";
  const addedAt = searchParams.get("added_at") || "";

  const { data: events = [], isLoading, error } = useQuery({
    queryKey: ["events", searchTerm, dtstart_utc, addedAt],
    queryFn: async () => {
      const queryParams: Record<string, string> = {};
      
      if (searchTerm) {
        queryParams.search = searchTerm;
      }
      
      if (dtstart_utc) {
        queryParams.dtstart_utc = formatDtstartToMidnight(dtstart_utc);
      }
      
      if (addedAt) {
        queryParams.added_at = addedAt;
      }

      return eventsAPIClient.getEvents(queryParams);
    },
    refetchOnWindowFocus: false,
    enabled: true,  
  });

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    let title: string;

    if (searchTerm) {
      title = `${events.length} Found Events - Wat2Do`;
    } else if (dtstart_utc) {
      title = `${events.length} Total Events - Wat2Do`;
    } else if (addedAt) {
      title = `${events.length} New Events - Wat2Do`;
    } else {
      title = `${events.length} Upcoming Events - Wat2Do`;
    }

    if (!isLoading) {
      previousTitleRef.current = title;
    }

    return previousTitleRef.current;
  }, [events.length, isLoading, searchTerm, dtstart_utc, addedAt]);

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

      if (dtstart_utc && dtstart_utc !== todayStr) {
        nextParams.delete("dtstart_utc");
      } else {
        nextParams.set("dtstart_utc", formatDtstartToMidnight("2025-01-01"));
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
        nextParams.delete("dtstart_utc");
      }
      return nextParams;
    });
  };

  return {
    events,
    isLoading,
    error,
    searchTerm,
    dtstart_utc,
    addedAt,
    handleViewChange,
    handleToggleStartDate,
    handleToggleNewEvents,
  };
}
