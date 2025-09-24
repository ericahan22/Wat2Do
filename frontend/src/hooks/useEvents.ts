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

  // Use static data when no filters, API data when filters are active
  const events = hasActiveFilters ? data?.events || [] : staticEventsData;

  return {
    data: events,
    uniqueCategories,
    isLoading: hasActiveFilters ? isLoading : false,
    error: hasActiveFilters ? error : null,
  };
}
