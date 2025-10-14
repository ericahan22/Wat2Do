import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { ClubsResponse } from "@/features/clubs/types/clubs";
import { API_BASE_URL } from "@/shared/constants/api";

const fetchClubs = async ({
  queryKey,
}: {
  queryKey: string[];
}): Promise<ClubsResponse> => {
  const searchTerm = queryKey[1] || "";
  const searchParam = searchTerm
    ? `&search=${encodeURIComponent(searchTerm)}`
    : "";
  const categoryFilter = queryKey[2] || "all";
  const categoryParam = categoryFilter
    ? `&category=${encodeURIComponent(categoryFilter)}`
    : "";

  const response = await fetch(
    `${API_BASE_URL}/clubs/?${searchParam}${categoryParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch clubs");
  }
  const data: ClubsResponse = await response.json();
  return data;
};

export function useClubs() {
  const [searchParams] = useSearchParams();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const { data, isLoading, error } = useQuery({
    queryKey: ["clubs", searchTerm, categoryFilter],
    queryFn: fetchClubs,
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
    data: data?.clubs || [],
    uniqueCategories,
    isLoading,
    error,
  };
}
