import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Tag, ExternalLink, Instagram, MessageCircle, Loader2 } from "lucide-react";
import { Club } from "@/features/clubs/types/clubs";
import { memo, useEffect, useRef } from "react";
import GeeveKickingRocks from "@/assets/artwork/geeve-kicking-rocks.svg?react";

interface ClubsGridProps {
  data: Club[];
  fetchNextPage?: () => void;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
}

const ClubsGrid = memo(({ data, fetchNextPage, hasNextPage, isFetchingNextPage }: ClubsGridProps) => {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Infinite scroll using Intersection Observer
  useEffect(() => {
    if (!fetchNextPage || !hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);
  return (
    <div className="space-y-8">
      {/* Clubs Grid */}
      <div className="grid xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-2.5">
        {data.map((club) => (
          <Card
            key={club.id}
            className="relative p-0 hover:shadow-lg gap-0 h-full overflow-hidden "
          >
            <CardHeader className="p-3.5 pb-0 gap-3">
              <CardTitle className="text-sm line-clamp-2 leading-tight text-gray-900 dark:text-white">
                {club.club_name}
              </CardTitle>
              {club.categories && club.categories.length > 0 && (
                <div className="flex gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <Tag className="h-3.5 w-3.5 flex-shrink-0" />
                  <span
                    className="line-clamp-2 text-xs"
                    title={club.categories.join(" | ")}
                  >
                    {club.categories.join(" | ")}
                  </span>
                </div>
              )}
            </CardHeader>
            <CardContent className="p-3.5 pt-2.5 gap-2 flex flex-col h-full">
              {/* Action Buttons */}
              <div className="flex pt-2 w-full mt-auto">
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
                    <ExternalLink className="h-4 w-4" />
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
                      <Instagram className="h-4 w-4" />
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
                      <MessageCircle className="h-4 w-4" />
                      Discord
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Infinite Scroll Loader */}
      {hasNextPage && (
        <div ref={loadMoreRef} className="flex justify-center py-8">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading more clubs...</span>
          </div>
        </div>
      )}

      {/* All clubs loaded message */}
      {data.length > 0 && !hasNextPage && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
          You've reached the end! 🎉
        </div>
      )}

      {/* No results message */}
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <GeeveKickingRocks className="w-32 h-32 mb-6 mx-auto text-gray-400 dark:text-gray-600" />
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
              No clubs found
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">
              Try adjusting your search or filters
            </p>
          </div>
        </div>
      )}
    </div>
  );
});

ClubsGrid.displayName = "ClubsGrid";

export default ClubsGrid;
