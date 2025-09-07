import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bookmark, ExternalLink, Instagram, MessageCircle } from "lucide-react";
import { Club } from "@/hooks";
import { memo } from "react";

interface ClubsGridProps {
  data: Club[];
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  infiniteScrollRef: (node?: Element | null) => void;
}

const ClubsGrid = memo(
  ({
    data,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef,
  }: ClubsGridProps) => {
    return (
      <div className="space-y-8">
        {/* Clubs Grid */}
        <div className="grid grid-cols-[repeat(auto-fit,_minmax(300px,_1fr))] gap-4 sm:gap-6">
          {data.map((club) => (
            <Card
              key={club.id}
              className="hover:shadow-lg h-full overflow-hidden bg-white"
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-lg line-clamp-2 leading-tight text-gray-900 dark:text-white">
                  {club.club_name}
                </CardTitle>
                {club.categories && club.categories.length > 0 && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                    <Bookmark className="h-4 w-4 flex-shrink-0" />
                    <span className="line-clamp-1" title={club.categories.join(" | ")}>
                      {club.categories.join(" | ")}
                    </span>
                  </div>
                )}
              </CardHeader>
              <CardContent className="space-y-3 flex flex-col h-full">
                {/* Action Buttons */}
                <div className="flex space-x-3 pt-2 w-full mt-auto">
                  {club.club_page ? (
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 w-full"
                      onMouseDown={() => {
                        // if club_page integer, append clubs.wusa.ca
                        const isInteger = /^\d+$/.test(club.club_page);
                        const url = isInteger
                          ? `https://clubs.wusa.ca/clubs/${club.club_page}`
                          : club.club_page;
                        window.open(url, "_blank");
                      }}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Website
                    </Button>
                  ) : (
                    <div className="text-center py-2 w-full">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        No website available
                      </p>
                    </div>
                  )}
                </div>

                {/* Social Links */}
                {(club.ig || club.discord) && (
                  <div className="flex space-x-3 w-full">
                    {club.ig && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 w-full"
                        onMouseDown={() =>
                          window.open(
                            `https://www.instagram.com/${club.ig}/`,
                            "_blank"
                          )
                        }
                      >
                        <Instagram className="h-4 w-4 mr-2" />
                        Instagram
                      </Button>
                    )}

                    {club.discord && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 w-full"
                        onMouseDown={() => window.open(club.discord, "_blank")}
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Discord
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Loading indicator for next page */}
        {hasNextPage && (
          <div
            ref={infiniteScrollRef}
            className="flex items-center justify-center py-8"
          >
            {isFetchingNextPage ? (
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
                <span>Loading more clubs...</span>
              </div>
            ) : (
              <div className="text-gray-500 dark:text-gray-400">
                Scroll to load more
              </div>
            )}
          </div>
        )}

        {/* No results message */}
        {data.length === 0 && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
                No clubs found
              </p>
              <p className="text-gray-400 dark:text-gray-500 text-sm">
                Try adjusting your search or filters
              </p>
            </div>
          </div>
        )}

        {/* End of results message */}
        {!hasNextPage && data.length > 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              You've reached the end of the list
            </p>
          </div>
        )}
      </div>
    );
  }
);

ClubsGrid.displayName = "ClubsGrid";

export default ClubsGrid;
