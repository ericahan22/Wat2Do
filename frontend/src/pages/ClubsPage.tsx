import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Bookmark, ExternalLink, Instagram, MessageCircle } from 'lucide-react'
import { useClubs } from '@/hooks'
import { useCategoryParam } from '@/hooks/useCategoryParam'
import SearchInput from '@/components/SearchInput'

function ClubsPage() {
  const {
    allClubs,
    filteredClubs,
    uniqueCategories,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef,
    totalCount,
  } = useClubs()

  const { categoryParam, setCategoryParam } = useCategoryParam()

  // Helper function to construct club page URL
  const getClubPageUrl = (clubPage: string) => {
    if (!clubPage) return null
    // Extract club page number from the URL if it's already a full URL
    const match = clubPage.match(/\/clubs\/(\d+)/)
    if (match) {
      return `https://clubs.wusa.ca/clubs/${match[1]}`
    }
    // If it's just a number, use it directly
    if (/^\d+$/.test(clubPage)) {
      return `https://clubs.wusa.ca/clubs/${clubPage}`
    }
    // If it's already a full URL starting with https://clubs.wusa.ca, use as is
    if (clubPage.startsWith('https://clubs.wusa.ca')) {
      return clubPage
    }
    // Otherwise, assume it's a club page number and prefix it
    return `https://clubs.wusa.ca/clubs/${clubPage}`
  }

  // Helper function to construct Instagram URL
  const getInstagramUrl = (igHandle: string) => {
    if (!igHandle) return null
    // If it's already a full URL, use as is
    if (igHandle.startsWith('https://')) {
      return igHandle
    }
    // Remove @ if present and prefix with Instagram URL
    const handle = igHandle.replace('@', '')
    return `https://www.instagram.com/${handle}`
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Clubs</h1>
        <p className="text-gray-600 dark:text-gray-400">Explore student clubs and organizations</p>
      </div>
      
      {/* Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput
            placeholder="Search clubs..."
            className="flex-1"
          />
          
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
            {filteredClubs.length} of {totalCount || allClubs.length} clubs matched
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
          <div className="text-lg text-red-600 dark:text-red-400">Error loading clubs: {error.message}</div>
        </div>
      )}

      {/* Clubs Grid */}
      {!isLoading && !error && (
        <div className="grid grid-cols-[repeat(auto-fit,_minmax(300px,_1fr))] gap-4 sm:gap-6">
          {filteredClubs.map((club) => (
            <Card 
              key={club.id} 
              className="hover:shadow-lg h-full overflow-hidden bg-white"
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-lg line-clamp-2 leading-tight text-gray-900 dark:text-white">{club.club_name}</CardTitle>
                {club.categories && club.categories.length > 0 && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                    <Bookmark className="h-4 w-4 flex-shrink-0" />
                    <span className="line-clamp-1">{club.categories.join(', ')}</span>
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
                      onMouseDown={() => window.open(getClubPageUrl(club.club_page) || '#', '_blank')}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Website
                    </Button>
                  ) : (
                    <div className="text-center py-2 w-full">
                      <p className="text-sm text-gray-500 dark:text-gray-400">No website available</p>
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
                        onMouseDown={() => window.open(getInstagramUrl(club.ig) || '#', '_blank')}
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
                        onMouseDown={() => window.open(club.discord, '_blank')}
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
      )}

      {/* Loading indicator for next page */}
      {hasNextPage && (
        <div ref={infiniteScrollRef} className="flex items-center justify-center py-8">
          {isFetchingNextPage ? (
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
              <span>Loading more clubs...</span>
            </div>
          ) : (
            <div className="text-gray-500 dark:text-gray-400">Scroll to load more</div>
          )}
        </div>
      )}

      {/* No results message */}
      {filteredClubs.length === 0 && !isLoading && !error && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">No clubs found</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">Try adjusting your search or filters</p>
          </div>
        </div>
      )}
      {/* End of results message */}
      {!hasNextPage && allClubs.length > 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">You've reached the end of the list</p>
        </div>
      )}
    </div>
  )
}

export default React.memo(ClubsPage) 
