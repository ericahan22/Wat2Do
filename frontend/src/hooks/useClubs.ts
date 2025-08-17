import { useState, useMemo, useEffect } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import { useSearchParams } from "react-router-dom";

export interface Club {
  id: number;
  club_name: string;
  categories: string[];
  club_page: string;
  ig: string;
  discord: string;
}

interface ClubsResponse {
  clubs: Club[];
  count: number;
  total_count: number;
  has_more: boolean;
  next_offset: number | null;
  current_offset: number;
  limit: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const fetchClubs = async ({ pageParam = 0, queryKey }: { pageParam?: number; queryKey: string[] }): Promise<ClubsResponse> => {
  const searchTerm = queryKey[1] || ""; // Get search term from queryKey
  const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : "";

  const response = await fetch(
    `${API_BASE_URL}/clubs/?limit=50&offset=${pageParam}${searchParam}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch clubs");
  }
  const data: ClubsResponse = await response.json();
  return data;
};

export function useClubs() {
  const [searchParams] = useSearchParams();
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const searchTerm = searchParams.get("search") || "";
  const categoryFilter = searchParams.get("category") || "all";

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ["clubs", searchTerm],  
    queryFn: fetchClubs,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.next_offset : undefined,
    initialPageParam: 0,
    refetchOnWindowFocus: false,
  });

  // Flatten all pages into a single array of clubs
  const allClubs = useMemo(() => {
    return data?.pages.flatMap((page) => page.clubs) || [];
  }, [data]);

  const filteredClubs = useMemo(() => {
    // Since search is now handled server-side, we only need to filter by category
    return allClubs.filter((club: Club) => {
      const matchesCategory =
        categoryFilter === "all" ||
        club.categories.some((category) =>
          category.toLowerCase().includes(categoryFilter.toLowerCase())
        );

      return matchesCategory;
    });
  }, [allClubs, categoryFilter]);

  const uniqueCategories = useMemo(() => {
    return [
      ...new Set(allClubs.flatMap((club: Club) => club.categories || [])),
    ].sort();
  }, [allClubs]);

  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: "200px",
  });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage && !isLoadingMore) {
      setIsLoadingMore(true);
      fetchNextPage().finally(() => {
        setTimeout(() => setIsLoadingMore(false), 500);
      });
    }
  }, [inView, hasNextPage, isFetchingNextPage, isLoadingMore, fetchNextPage]);

  return {
    allClubs,
    filteredClubs,
    uniqueCategories,    
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef: ref,
    totalCount: data?.pages[0]?.total_count,
  };
}
