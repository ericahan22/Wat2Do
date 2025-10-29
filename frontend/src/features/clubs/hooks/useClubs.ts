import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useApi } from "@/shared/hooks/useApi";
import type { ClubsResponse } from "@/shared/api";

export function useClubs() {
  const [searchParams] = useSearchParams();
  const { clubs } = useApi();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const { data, isLoading, error } = useQuery({
    queryKey: ["clubs", searchTerm, categoryFilter],
    queryFn: async () => {
      const queryParams: Record<string, string> = {};
      
      if (searchTerm) {
        queryParams.search = searchTerm;
      }
      
      if (categoryFilter && categoryFilter !== "all") {
        queryParams.category = categoryFilter;
      }

      return clubs.getClubs(queryParams);
    },
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
