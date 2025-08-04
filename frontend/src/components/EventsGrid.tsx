import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar, Clock, MapPin, ExternalLink, Eye, EyeOff } from 'lucide-react'
import { Event } from '@/hooks'
import { memo, useState } from 'react'

interface EventsGridProps {
  events: Event[]
  allEvents: Event[]
  hasNextPage: boolean
  isFetchingNextPage: boolean
  infiniteScrollRef: (node?: Element | null) => void
  formatDate: (dateString: string) => string
  formatTime: (timeString: string) => string
}

const EventsGrid = memo(({
  events,
  allEvents,
  hasNextPage,
  isFetchingNextPage,
  infiniteScrollRef,
  formatDate,
  formatTime,
}: EventsGridProps) => {
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set())

  const toggleEventExpansion = (eventId: number) => {
    const newExpanded = new Set(expandedEvents)
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId)
    } else {
      newExpanded.add(eventId)
    }
    setExpandedEvents(newExpanded)
  }

  return (
    <div className="space-y-8">
      {/* Events Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(500px,_1fr))] gap-4 sm:gap-6">
        {events.map((event) => {
          const isExpanded = expandedEvents.has(event.id)
          
          return (
            <Card 
              key={event.id} 
              className="hover:shadow-lg h-full overflow-hidden bg-white"
            >
              <CardHeader className="pb-1">
                <CardTitle className="text-lg line-clamp-2 leading-tight text-gray-900 dark:text-white">{event.name}</CardTitle>
                <p className="text-sm text-gray-600 dark:text-gray-400">@{event.club_handle}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <Calendar className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">{formatDate(event.date)}</span>
                </div>
                
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <Clock className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">
                    {formatTime(event.start_time)} - {formatTime(event.end_time)}
                  </span>
                </div>
                
                {event.location && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                    <MapPin className="h-4 w-4 flex-shrink-0" />
                    <span className="line-clamp-1">{event.location}</span>
                  </div>
                )}
                
                {/* Action Buttons */}
                <div className="flex space-x-3 pt-2 w-full">
                  {event.url ? (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 w-full"
                        onMouseDown={() => toggleEventExpansion(event.id)}
                      >
                        {isExpanded ? (
                          <>
                            <EyeOff className="h-4 w-4 mr-2" />
                            Hide
                          </>
                        ) : (
                          <>
                            <Eye className="h-4 w-4 mr-2" />
                            Preview
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 w-full"
                        onMouseDown={() => window.open(event.url, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Open
                      </Button>
                    </>
                  ) : (
                    <div className="text-center py-2 w-full">
                      <p className="text-sm text-gray-500 dark:text-gray-400">No preview available</p>
                    </div>
                  )}
                </div>

                {/* Iframe Embed */}
                {isExpanded && event.url && (
                  <div className="mt-4 border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden">
                    <iframe
                      src={event.url}
                      title={event.name}
                      className="w-full h-64 border-0"
                      loading="lazy"
                      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Loading indicator for next page */}
      {hasNextPage && (
        <div ref={infiniteScrollRef} className="flex items-center justify-center py-8">
          {isFetchingNextPage ? (
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
              <span>Loading more events...</span>
            </div>
          ) : (
            <div className="text-gray-500 dark:text-gray-400">Scroll to load more</div>
          )}
        </div>
      )}

      {/* No results message */}
      {events.length === 0 && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">No events found</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">Try adjusting your search or filters</p>
          </div>
        </div>
      )}

      {/* End of results message */}
      {!hasNextPage && allEvents.length > 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">You've reached the end of the list</p>
        </div>
      )}
    </div>
  )
})

EventsGrid.displayName = 'EventsGrid'

export default EventsGrid 