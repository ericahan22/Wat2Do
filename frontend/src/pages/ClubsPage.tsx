import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Bookmark, ExternalLink, Instagram, MessageCircle } from 'lucide-react'
import { useClubs } from '@/hooks'
import { useSearchParam } from '@/hooks/useSearchParam'
import { useCategoryParam } from '@/hooks/useCategoryParam'

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

  const { searchValue, setSearchValue } = useSearchParam()
  const { categoryParam, setCategoryParam } = useCategoryParam()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg text-gray-900 dark:text-gray-100">Loading clubs...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg text-red-600 dark:text-red-400">Error loading clubs: {error.message}</div>
      </div>
    )
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
          <Input
            placeholder="Search clubs..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
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
            Showing {filteredClubs.length} of {allClubs.length} clubs
            {totalCount && allClubs.length < totalCount && (
              <span className="ml-1">({totalCount} total available)</span>
            )}
          </p>
        </div>
      </div>

      {/* Clubs Grid */}
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
                    onMouseDown={() => window.open(club.club_page, '_blank')}
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
                      onMouseDown={() => window.open(club.ig, '_blank')}
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
      {filteredClubs.length === 0 && !isLoading && (
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
