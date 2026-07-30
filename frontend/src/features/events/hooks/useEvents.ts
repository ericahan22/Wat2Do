import { useMemo, useRef } from "react";
import { useInfiniteQuery, type InfiniteData } from "@tanstack/react-query";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useDocumentTitle } from "@/shared/hooks/useDocumentTitle";
import { useApi } from "@/shared/hooks/useApi";
import { useMyInterestedEvents } from "./useEventInterest";
import { DEFAULT_SCHOOL } from "@/shared/lib/school";
import { useAuthState } from "@/features/auth/hooks/useAuthState";
import type { EventsResponse, EventsQueryParams } from "@/shared/api/EventsAPIClient";
import type { Event } from "@/features/events";

const ALL_EVENTS_START_UTC = "1970-01-01T00:00:00Z";

export function useEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isSignedIn } = useAuthState();
  const { eventsAPIClient } = useApi();
  const searchTerm = searchParams.get("search") || "";
  const categories = searchParams.get("categories") || "";
  const addedAt = searchParams.get("added_at") || "";
  const showAll = searchParams.get("all") === "true";
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
  } = useInfiniteQuery<
    EventsResponse,
    Error,
    EventsResponse,
    string[],
    string | undefined
  >({
    queryKey: [
      "events",
      searchTerm,
      categories,
      addedAt,
      showAll ? "all" : "",
      view,
      DEFAULT_SCHOOL,
      showInterested ? "interested" : "",
    ],
    queryFn: async ({ pageParam }: { pageParam: string | undefined }) => {
      const queryParams: EventsQueryParams = {
        school_id: DEFAULT_SCHOOL,
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

      if (addedAt) {
        queryParams.added_at = addedAt;
      }

      if (showAll) {
        queryParams.start_utc = ALL_EVENTS_START_UTC;
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
    const infiniteData = data as unknown as InfiniteData<EventsResponse> | undefined;
    if (!infiniteData?.pages) return [];
    return infiniteData.pages.flatMap((page: EventsResponse) => page.results);
  }, [data]);

  // Filter events by interested if the filter is active
  const filteredEvents = useMemo(() => {
    if (showInterested && interestedEventIds) {
      return events.filter((event: Event) => interestedEventIds.has(event.id));
    }
    return events;
  }, [events, showInterested, interestedEventIds]);

  const previousTitleRef = useRef<string>("Events - Wat2Do");

  const documentTitle = useMemo(() => {
    const displayCount = filteredEvents.length;
    let title: string;

    if (searchTerm || categories) {
      title = `${displayCount} Found Events - Wat2Do`;
    } else if (showInterested) {
      title = `${displayCount} Interested Events - Wat2Do`;
    } else if (showAll) {
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
  }, [
    filteredEvents.length,
    isLoading,
    searchTerm,
    categories,
    addedAt,
    showAll,
    showInterested,
  ]);

  useDocumentTitle(documentTitle);

  const handleViewChange = (newView: string) => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.set("view", newView);
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
      }
      return nextParams;
    });
  };

  const handleToggleAllEvents = () => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);

      if (showAll) {
        nextParams.delete("all");
      } else {
        nextParams.set("all", "true");
      }

      return nextParams;
    });
  };

  const handleToggleInterested = () => {
    // Redirect to sign-in if user is not authenticated
    if (!isSignedIn) {
      navigate("/login");
      return;
    }

    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);

      if (showInterested) {
        // When deselecting interested, remove all filters to show upcoming events
        nextParams.delete("interested");
      } else {
        nextParams.set("interested", "true");
      }
      return nextParams;
    });
  };

  const clearAllFilters = () => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      // Keep only the view parameter
      const currentView = nextParams.get("view");
      nextParams.delete("search");
      nextParams.delete("categories");
      nextParams.delete("dtstart_utc");
      nextParams.delete("all");
      nextParams.delete("added_at");
      nextParams.delete("interested");
      if (currentView) {
        nextParams.set("view", currentView);
      }
      return nextParams;
    });
  };

  return {
    events: filteredEvents,
    isLoading,
    error,
    searchTerm,
    categories,
    addedAt,
    showAll,
    showInterested,
    handleViewChange,
    handleToggleNewEvents,
    handleToggleAllEvents,
    handleToggleInterested,
    clearAllFilters,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  };
}
