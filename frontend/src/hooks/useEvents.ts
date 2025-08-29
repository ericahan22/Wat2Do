import { useState, useMemo, useEffect } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import { useSearchParams } from "react-router-dom";

export interface Event {
  id: number;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  categories?: string[];
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const fetchEvents = async ({ pageParam = 0, queryKey }: { pageParam?: number; queryKey: string[] }): Promise<EventsResponse> => {
  const searchTerm = queryKey[1] || ""; // Get search term from queryKey
  const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : "";

  const response = await fetch(
    `${API_BASE_URL}/events/?limit=50&offset=${pageParam}${searchParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: EventsResponse = await response.json();
  return data;
};

export function useEvents() {
  const [searchParams] = useSearchParams();
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

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
    refetchOnWindowFocus: false,
  });

  // Flatten all pages into a single array of events
  const allEvents = useMemo(() => {
    return data?.pages.flatMap((page) => page.events) || [];
  }, [data]);

  const filteredEvents = useMemo(() => {
    // Since search is now handled server-side, we only need to filter by category
    return allEvents.filter((event: Event) => {
      const matchesCategory =
        categoryFilter === "all" ||
        (event.categories && event.categories.some((category) =>
          category.toLowerCase().includes(categoryFilter.toLowerCase())
        ));

      return matchesCategory;
    });
  }, [allEvents, categoryFilter]);

  const uniqueCategories = useMemo(() => {
    return [
      'Academic',
      'Business and Entrepreneurial',
      'Charitable, Community Service & International Development',
      'Creative Arts, Dance and Music',
      'Cultural',
      'Environmental and Sustainability',
      'Games, Recreational and Social',
      'Health Promotion',
      'Media, Publications and Web Development',
      'Political and Social Awareness',
      'Religious and Spiritual'
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

  return {
    allEvents,
    filteredEvents,
    uniqueCategories,    
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef: ref,
    totalCount: data?.pages[0]?.total_count,
  };
}
