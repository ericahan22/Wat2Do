import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useClubs } from "@/hooks";
import ClubsGrid from "@/components/ClubsGrid";
import SearchInput from "@/components/SearchInput";
import { memo } from "react";

const ClubsPage = memo(() => {
  const {
    allClubs,
    filteredClubs,
    uniqueCategories,
    handleSearch,
    categoryFilter,
    setCategoryFilter,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef,
    totalCount,
  } = useClubs();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Clubs
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {totalCount
            ? `Explore ${totalCount} student clubs and organizations`
            : "Loading clubs..."}
        </p>
      </div>

      {/* Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput onSearch={handleSearch} placeholder="Search clubs..." />

          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
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
      </div>

      {/* Content Area - Shows loading, error, or clubs grid */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="text-lg text-gray-900 dark:text-gray-100">
            Loading clubs...
          </div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="text-lg text-red-600 dark:text-red-400">
            Error loading clubs: {error.message}
          </div>
        </div>
      ) : (
        <ClubsGrid
          clubs={filteredClubs}
          allClubs={allClubs}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
          infiniteScrollRef={infiniteScrollRef}
        />
      )}
    </div>
  );
});

ClubsPage.displayName = "ClubsPage";

export default ClubsPage;
