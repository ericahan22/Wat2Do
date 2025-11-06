import { useMemo, useRef } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "@clerk/clerk-react";
import { useDocumentTitle } from "@/shared/hooks/useDocumentTitle";
import { useApi } from "@/shared/hooks/useApi";
import { getTodayString, formatDtstartToMidnight } from "@/shared/lib/dateUtils";
import { useMyInterestedEvents } from "./useEventInterest";
import { EventsResponse } from "@/shared/api/EventsAPIClient";
import { Event } from "@/features/events";

export function useEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isSignedIn } = useAuth();
  const { eventsAPIClient } = useApi();
  const searchTerm = searchParams.get("search") || "";
  const categories = searchParams.get("categories") || "";
  const dtstart_utc = searchParams.get("dtstart_utc") || "";
  const addedAt = searchParams.get("added_at") || "";
  const showInterested = searchParams.get("interested") === "true";
  const view = searchParams.get("view") || "grid";
  
  const { data: interestedEventIds } = useMyInterestedEvents();

  const { 
    data,
    isLoading, 
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery<EventsResponse, Error, any, string[], string | undefined>({
    queryKey: ["events", searchTerm, categories, dtstart_utc, addedAt, view, showInterested ? "interested" : ""],
    queryFn: async ({ pageParam }: { pageParam: string | undefined }) => {
      const queryParams: Record<string, any> = {
        limit: 15, // Load 15 events at a time
      };
      
      if (pageParam) {
        queryParams.cursor = pageParam;
      }
      
      if (searchTerm) {
        queryParams.search = searchTerm;
      }
      
      if (categories) {
        queryParams.categories = categories;
      }
      
      if (dtstart_utc) {
        queryParams.dtstart_utc = formatDtstartToMidnight(dtstart_utc);
      }
      
      if (addedAt) {
        queryParams.added_at = addedAt;
      }

      // For calendar view, fetch all events
      if (view === "calendar") {
        queryParams.all = true;
      }

      // When viewing Interested, reveal all interested from 2025-01-01
      if (showInterested) {
        queryParams.all = true;
        queryParams.dtstart_utc = formatDtstartToMidnight("2025-01-01");
      }

      return eventsAPIClient.getEvents(queryParams);
    },
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    refetchOnWindowFocus: false,
    enabled: true,  
  });

  // Flatten all pages into a single array of events
  const events = useMemo(() => {
    if (!data?.pages) return [];
    return data.pages.flatMap((page: EventsResponse) => page.results);
  }, [data]);

  // Get total count from first page
  const totalCount = (data?.pages?.[0] as EventsResponse | undefined)?.totalCount ?? 0;

  // Filter events by interested if the filter is active
  const filteredEvents = useMemo(() => {
    if (showInterested && interestedEventIds) {
      return events.filter((event: Event) => interestedEventIds.has(event.id));
    }
    return events;
  }, [events, showInterested, interestedEventIds]);

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    let title: string;
    
    // Use totalCount if available and not filtering by interested (which filters client-side)
    const displayCount = showInterested ? filteredEvents.length : totalCount || filteredEvents.length;

    if (searchTerm || categories) {
      title = `${displayCount} Found Events - Wat2Do`;
    } else if (showInterested) {
      title = `${displayCount} Interested Events - Wat2Do`;
    } else if (dtstart_utc) {
      title = `${displayCount} Total Events - Wat2Do`;
    } else if (addedAt) {
      title = `${displayCount} New Events - Wat2Do`;
    } else {
      title = `${displayCount} Upcoming Events - Wat2Do`;
    }

    if (!isLoading) {
      previousTitleRef.current = title;
    }

    return previousTitleRef.current;
  }, [filteredEvents.length, totalCount, isLoading, searchTerm, categories, dtstart_utc, addedAt, showInterested]);

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
        nextParams.delete("interested");
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
        const cutoffDate = new Date(now.getTime() - 24 * 60 * 60 * 1000); // past 24 hours
        const isoString = cutoffDate.toISOString();
        nextParams.set("added_at", isoString);
        nextParams.delete("dtstart_utc");
        nextParams.delete("interested");
      }
      return nextParams;
    });
  };

  const handleToggleInterested = () => {
    // Redirect to sign-in if user is not authenticated
    if (!isSignedIn) {
      navigate("/auth/sign-in");
      return;
    }

    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);

      if (showInterested) {
        // When deselecting interested, remove all filters to show upcoming events
        nextParams.delete("interested");
        nextParams.delete("dtstart_utc");
        nextParams.delete("added_at");
      } else {
        nextParams.set("interested", "true");
        // Reveal all interested from 2025-01-01
        nextParams.set("dtstart_utc", formatDtstartToMidnight("2025-01-01"));
        nextParams.delete("added_at");
      }
      return nextParams;
    });
  };

  return {
    events: filteredEvents,
    totalCount,
    isLoading,
    error,
    searchTerm,
    categories,
    dtstart_utc,
    addedAt,
    showInterested,
    handleViewChange,
    handleToggleStartDate,
    handleToggleNewEvents,
    handleToggleInterested,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  };
}
