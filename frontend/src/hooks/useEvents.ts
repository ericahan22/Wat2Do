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
}

interface EventsResponse {
  event_ids: string[];
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const fetchEvents = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<EventsResponse> => {
  const searchTerm = queryKey[1] || "";
  const searchParam = searchTerm
    ? `?search=${encodeURIComponent(searchTerm)}`
    : "";

  const response = await fetch(
    `${API_BASE_URL}/api/events/${searchParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }
  const data: EventsResponse = await response.json();
  return data;
};

export function useEvents(view: "grid" | "calendar") {
  const [searchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";

  const hasActiveFilters = searchTerm !== "";

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
  });


  // Get events from static data using IDs from search results
  const events = useMemo(() => {
    let rawEvents: Event[];
    
    if (hasActiveFilters && data?.event_ids) {
      rawEvents = data.event_ids
        .map(id => staticEventsData[id])
    } else { 
      rawEvents = Object.values(staticEventsData);
    }

    if (view === "grid") {
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
    }
    
    // For calendar view, return all events (backend already sorted them)
    return rawEvents;
  }, [hasActiveFilters, data?.event_ids, view]);

  return {
    data: events,
    isLoading: hasActiveFilters ? isLoading : false,
    error: hasActiveFilters ? error : null,
  };
}
