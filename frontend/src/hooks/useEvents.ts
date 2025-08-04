import { useState, useMemo, useEffect, useCallback } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import debounce from "lodash/debounce";

export interface Event {
  id: number;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
}

interface EventsResponse {
  events: Event[];
  count: number;
  total_count: number;
  has_more: boolean;
  next_offset: number | null;
  current_offset: number;
  limit: number;
}

const fetchEvents = async ({
  pageParam = 0,
  queryKey,
}: {
  pageParam?: number;
  queryKey: any[];
}): Promise<EventsResponse> => {
  const searchTerm = queryKey[1] || "";
  const searchParam = searchTerm
    ? `&search=${encodeURIComponent(searchTerm)}`
    : "";

  const response = await fetch(
    `http://localhost:8000/api/events/?limit=50&offset=${pageParam}${searchParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  return response.json();
};

export function useEvents() {
  const [searchTerm, setSearchTerm] = useState("");
  const [timeFilter, setTimeFilter] = useState("This week");
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ["events", searchTerm],
    queryFn: fetchEvents,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.next_offset : undefined,
    initialPageParam: 0,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  // Flatten all pages into a single array of events
  const allEvents = useMemo(() => {
    return data?.pages.flatMap((page) => page.events) || [];
  }, [data]);

  const filteredEvents = useMemo(() => {
    return allEvents.filter((event: Event) => {
      // Time-based filtering
      if (!event.date) return true;

      const eventDate = new Date(event.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      // Calculate time period boundaries
      const startOfWeek = new Date(today);
      startOfWeek.setDate(today.getDate() - today.getDay());
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(startOfWeek.getDate() + 6);
      endOfWeek.setHours(23, 59, 59, 999);

      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      endOfMonth.setHours(23, 59, 59, 999);

      const startOfYear = new Date(today.getFullYear(), 0, 1);
      const endOfYear = new Date(today.getFullYear(), 11, 31);
      endOfYear.setHours(23, 59, 59, 999);

      const endOfToday = new Date(today);
      endOfToday.setHours(23, 59, 59, 999);

      let matchesTime = true;
      switch (timeFilter) {
        case "This week":
          matchesTime = eventDate >= startOfWeek && eventDate <= endOfWeek;
          break;
        case "This month":
          matchesTime = eventDate >= startOfMonth && eventDate <= endOfMonth;
          break;
        case "This year":
          matchesTime = eventDate >= startOfYear && eventDate <= endOfYear;
          break;
        case "All time":
          matchesTime = true;
          break;
      }

      return matchesTime;
    });
  }, [allEvents, timeFilter]);

  const uniqueTimes = useMemo(() => {
    return [
      "This week",
      "This month",
      "This year",
      "All time",
    ];
  }, []);

  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: "200px",
  });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage && !isLoadingMore) {
      setIsLoadingMore(true);
      fetchNextPage().finally(() => {
        setTimeout(() => setIsLoadingMore(false), 500);
      });
    }
  }, [inView, hasNextPage, isFetchingNextPage, isLoadingMore, fetchNextPage]);

  const handleSearch = (searchValue: string) => {
    setSearchTerm(searchValue);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "TBD";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatTime = (timeString: string) => {
    if (!timeString) return "TBD";
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  return {
    // Data
    allEvents,
    filteredEvents,
    uniqueTimes,

    // State
    searchTerm,
    handleSearch,
    timeFilter,
    setTimeFilter,

    // Query state
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,

    // Infinite scrolling
    infiniteScrollRef: ref,

    // Metadata
    totalCount: data?.pages[0]?.total_count,

    // Utility functions
    formatDate,
    formatTime,
  };
}
