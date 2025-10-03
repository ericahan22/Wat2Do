import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { staticEventsData } from "@/data/staticEvents";

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
  reactions?: Record<string, number>;
  user_reaction?: string;
}

interface EventsResponse {
  event_ids: string[];
}

type ReactionsResponse = Record<string, Record<string, number>>;

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const fetchEvents = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<EventsResponse> => {
  const searchTerm = queryKey[1] || "";
  const searchParam = searchTerm
    ? `&search=${encodeURIComponent(searchTerm)}`
    : "";
  const categoryFilter = queryKey[2] || "all";
  const categoryParam = categoryFilter
    ? `&category=${encodeURIComponent(categoryFilter)}`
    : "";
  const view = queryKey[3] || "grid";

  const response = await fetch(
    `${API_BASE_URL}/api/events/?view=${view}${searchParam}${categoryParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: EventsResponse = await response.json();
  return data;
};

const fetchReactions = async (): Promise<ReactionsResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/reactions/`);
  if (!response.ok) {
    console.error("Failed to fetch (live) reactions");
    return {};
  }
  return response.json();
};

export function useEvents(view: "grid" | "calendar") {
  const [searchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const hasActiveFilters = searchTerm !== "" || categoryFilter !== "all";

  const { 
    data: eventsData, 
    isLoading: isLoadingEvents,
    error: eventsError
   } = useQuery({
    queryKey: ["events", searchTerm, categoryFilter, view],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
  });

  const { data: reactionsData, isLoading: isLoadingReactions } = useQuery({
    queryKey: ["reactions"],
    queryFn: fetchReactions,
    refetchOnWindowFocus: true,
    staleTime: 60 * 1000,
  });

  const uniqueCategories = useMemo(() => {
    return [
      "Academic",
      "Athletics",
      "Business and Entrepreneurial",
      "Charitable, Community Service & International Development",
      "Creative Arts, Dance and Music",
      "Cultural",
      "Environmental and Sustainability",
      "Games, Recreational and Social",
      "Health Promotion",
      "Media, Publications and Web Development",
      "Political and Social Awareness",
      "Religious and Spiritual",
    ];
  }, []);

  // Get events from static data using IDs from search results
  const events = useMemo(() => {
    let rawEvents: Event[];
    
    if (hasActiveFilters && eventsData?.event_ids) {
      // Get events from static data using the returned IDs
      rawEvents = eventsData.event_ids
        .map(id => staticEventsData[id]) 
    } else { 
      rawEvents = Object.values(staticEventsData);
    }

    const eventsWithLiveReactions = rawEvents.map((event) => ({
      ...event,
      reactions: reactionsData?.[event.id] || event.reactions || {},
    }));

    if (view === "grid") {
      const now = new Date();
      const todayStr =
        now.getFullYear() +
        "-" +
        String(now.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(now.getDate()).padStart(2, "0");
        
      return eventsWithLiveReactions
        .filter((event) => {
          const eventDateStr = event.date; // e.g., "2025-09-24"

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
        })
        .sort((a, b) => {
          const dateA = new Date(a.date);
          const dateB = new Date(b.date);

          // First sort by date
          const dateDiff = dateA.getTime() - dateB.getTime();
          if (dateDiff !== 0) {
            return dateDiff;
          }

          // If same date, sort by start time
          const [hoursA, minutesA] = a.start_time.split(":").map(Number);
          const [hoursB, minutesB] = b.start_time.split(":").map(Number);
          const timeA = hoursA * 60 + minutesA; // Convert to minutes for easy comparison
          const timeB = hoursB * 60 + minutesB;

          return timeA - timeB;
        });
    }
    return eventsWithLiveReactions;
  }, [hasActiveFilters, eventsData?.event_ids, view, reactionsData]);

  return {
    data: events,
    uniqueCategories,
    isLoading: hasActiveFilters ? isLoadingEvents : isLoadingReactions,
    error: hasActiveFilters ? eventsError : null,
  };
}
