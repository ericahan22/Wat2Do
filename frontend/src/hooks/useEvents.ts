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
  events: Event[];
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

export function useEvents(view: "grid" | "calendar") {
  const [searchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const hasActiveFilters = searchTerm !== "" || categoryFilter !== "all";

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm, categoryFilter, view],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
    enabled: hasActiveFilters,
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

  // Filter out past events and sort by date for grid view
  const events = useMemo(() => {
    const rawEvents = hasActiveFilters ? data?.events || [] : staticEventsData;

    if (view === "grid") {
      const now = new Date();
      const todayStr =
        now.getFullYear() +
        "-" +
        String(now.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(now.getDate()).padStart(2, "0");
        
      return rawEvents
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
    return rawEvents;
  }, [hasActiveFilters, data?.events, view]);

  return {
    data: events,
    uniqueCategories,
    isLoading: hasActiveFilters ? isLoading : false,
    error: hasActiveFilters ? error : null,
  };
}
