import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
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
  price?: number | null;
  food?: string | null;
  registration?: boolean;
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
    `${API_BASE_URL}/events/?view=${view}${searchParam}${categoryParam}`
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

  const { data, isLoading, error } = useQuery({
    queryKey: ["events", searchTerm, categoryFilter, view],
    queryFn: fetchEvents,
    refetchOnWindowFocus: false,
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

  return {
    data: data?.events || [],
    uniqueCategories,
    isLoading,
    error,
  };
}
