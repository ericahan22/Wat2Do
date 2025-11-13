import { useMemo } from "react";
import { useInfiniteQuery, type InfiniteData } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useApi } from "@/shared/hooks/useApi";
import type { ClubsResponse } from "@/shared/api";

export function useClubs() {
  const [searchParams] = useSearchParams();
  const { clubsAPIClient } = useApi();
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery<ClubsResponse, Error, ClubsResponse, string[], string | undefined>({
    queryKey: ["clubs", searchTerm, categoryFilter],
    queryFn: async ({ pageParam }: { pageParam: string | undefined }) => {
      const queryParams: Record<string, string | undefined> = {};
      
      if (pageParam) {
        queryParams.cursor = pageParam;
      }
      
      if (searchTerm) {
        queryParams.search = searchTerm;
      }
      
      if (categoryFilter && categoryFilter !== "all") {
        queryParams.category = categoryFilter;
      }

      return clubsAPIClient.getClubs(queryParams);
    },
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    refetchOnWindowFocus: false,
    enabled: true,
  });

  // Flatten all pages into a single array of clubs
  const clubs = useMemo(() => {
    const infiniteData = data as unknown as InfiniteData<ClubsResponse> | undefined;
    if (!infiniteData?.pages) return [];
    return infiniteData.pages.flatMap((page: ClubsResponse) => page.results);
  }, [data]);

  // Get total count from first page
  const totalCount = ((data as unknown as InfiniteData<ClubsResponse>)?.pages?.[0] as ClubsResponse | undefined)?.totalCount ?? 0;

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
    data: clubs,
    totalCount,
    uniqueCategories,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  };
}
