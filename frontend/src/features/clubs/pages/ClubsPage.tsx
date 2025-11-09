import { useMemo, useRef } from "react";
import NumberFlow from "@number-flow/react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, useDocumentTitle, useCategoryParam, SEOHead } from "@/shared";
import { useClubs, ClubsGrid } from "@/features/clubs";
import SearchInput from "@/features/search/components/SearchInput";

function ClubsPage() {
  const {
    data,
    totalCount,
    uniqueCategories,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useClubs();

  const { categoryParam, setCategoryParam } = useCategoryParam();

  const previousTitleRef = useRef<string>("Clubs - Wat2Do");

  const documentTitle = useMemo(() => {
    const title = `${totalCount} Total Clubs - Wat2Do`;
    
    if (!isLoading) {
      previousTitleRef.current = title;
    }
    
    return previousTitleRef.current;
  }, [totalCount, isLoading]);

  useDocumentTitle(documentTitle);

  return (
    <div className="flex flex-col gap-4">
      <SEOHead 
        title="Clubs - University of Waterloo Student Organizations"
        description="Explore student clubs and organizations at the University of Waterloo. Discover campus clubs, find your interests, and connect with like-minded students."
        url="/clubs"
        keywords={[
          'University of Waterloo clubs',
          'UW student organizations',
          'campus clubs',
          'student clubs',
          'Waterloo university clubs',
          'club directory',
          'student organizations',
          'campus groups'
        ]}
      />
      <div className="sm:text-left">
        <h1 className="sm:text-3xl text-2xl font-bold mb-2">
          <NumberFlow value={totalCount} suffix={" clubs"} />
        </h1>
        <p className="text-gray-600 dark:text-gray-400">Explore student clubs and organizations</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4">
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
            {isLoading ? "Loading..." : `Showing ${data.length} of ${totalCount} clubs`}
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


      {/* Clubs Grid */}
      {!isLoading && !error && (
        <ClubsGrid
          data={data}
          fetchNextPage={fetchNextPage}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
        />
      )}
    </div>
  );
}

export default ClubsPage;
