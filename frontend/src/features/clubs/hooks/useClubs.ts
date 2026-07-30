import { useMemo } from "react";
import { useInfiniteQuery, type InfiniteData } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useApi } from "@/shared/hooks/useApi";
import type { ClubsResponse } from "@/shared/api";
import { DEFAULT_SCHOOL } from "@/shared/lib/school";

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
    queryKey: ["clubs", searchTerm, categoryFilter, DEFAULT_SCHOOL],
    queryFn: async ({ pageParam }: { pageParam: string | undefined }) => {
      const queryParams: Record<string, string | undefined> = {};
      queryParams.school = DEFAULT_SCHOOL;
      
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
    return Array.from(new Set(clubs.flatMap((club) => club.categories))).sort();
  }, [clubs]);

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
