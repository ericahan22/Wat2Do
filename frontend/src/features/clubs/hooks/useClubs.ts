import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { clubsAPIClient } from "@/shared/api";
import type { Club, ClubsResponse } from "@/shared/api";

const fetchClubs = async (params: {
  searchTerm?: string;
  categoryFilter?: string;
}): Promise<Club[]> => {
  const queryParams: Record<string, string> = {};
  
  if (params.searchTerm) {
    queryParams.search = params.searchTerm;
  }
  
  if (params.categoryFilter && params.categoryFilter !== "all") {
    queryParams.category = params.categoryFilter;
  }

  return clubsAPIClient.getClubs(queryParams);
};

export function useClubs() {
  const [searchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const { data, isLoading, error } = useQuery({
    queryKey: ["clubs", searchTerm, categoryFilter],
    queryFn: () => fetchClubs({ searchTerm, categoryFilter }),
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
    data: (data as unknown as ClubsResponse)?.clubs ?? [],
    uniqueCategories,
    isLoading,
    error,
  };
}
