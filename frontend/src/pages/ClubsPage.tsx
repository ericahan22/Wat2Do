import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useClubs } from "@/hooks";
import { useCategoryParam } from "@/hooks/useCategoryParam";
import SearchInput from "@/components/SearchInput";
import ClubsGrid from "@/components/ClubsGrid";

function ClubsPage() {
  const {
    data,
    uniqueCategories,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef,
    totalCount,
    totalQueryCount,
  } = useClubs();

  const { categoryParam, setCategoryParam } = useCategoryParam();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Clubs
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Explore student clubs and organizations
        </p>
      </div>

      {/* Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput placeholder="Search clubs..." className="flex-1" />

          <Select value={categoryParam} onValueChange={setCategoryParam}>
            <SelectTrigger className="w-full sm:w-auto">
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {uniqueCategories.map((category: string) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLoading ? "Loading..." : `${totalQueryCount || 0} of ${totalCount || 0} clubs results`}
          </p>
        </div>
      </div>

      {/* Loading state - show content with loading indicator */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <span>Loading clubs...</span>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex items-center justify-center py-8">
          <div className="text-lg text-red-600 dark:text-red-400">
            Error loading clubs: {error.message}
          </div>
        </div>
      )}

      {/* Clubs Grid */}
      {!isLoading && !error && (
        <ClubsGrid
          data={data}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
          infiniteScrollRef={infiniteScrollRef}
        />
      )}
    </div>
  );
}

export default React.memo(ClubsPage);
