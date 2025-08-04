import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Calendar, Clock, MapPin, ExternalLink, Eye, EyeOff } from 'lucide-react'

interface Event {
  id: number
  club_handle: string
  url: string
  name: string
  date: string
  start_time: string
  end_time: string
  location: string
}

interface EventsResponse {
  events: Event[]
}

const fetchEvents = async (): Promise<Event[]> => {
  const response = await fetch('http://localhost:8000/api/events/')
  if (!response.ok) {
    throw new Error('Failed to fetch events')
  }
  const data: EventsResponse = await response.json()
  return data.events || []
}

export default function EventsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [timeFilter, setTimeFilter] = useState('today')
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set())

  const { data: events = [], isLoading, error } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents,
  })

  const filteredEvents = events.filter((event: Event) => {
    const matchesSearch = !searchTerm || 
      event.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.club_handle.toLowerCase().includes(searchTerm.toLowerCase())
    
    // Time-based filtering
    if (!event.date) return matchesSearch
    
    const eventDate = new Date(event.date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const startOfWeek = new Date(today)
    startOfWeek.setDate(today.getDate() - today.getDay())
    
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const startOfYear = new Date(today.getFullYear(), 0, 1)
    
    let matchesTime = true
    switch (timeFilter) {
      case 'today':
        matchesTime = eventDate.getTime() === today.getTime()
        break
      case 'week':
        matchesTime = eventDate >= startOfWeek && eventDate <= today
        break
      case 'month':
        matchesTime = eventDate >= startOfMonth && eventDate <= today
        break
      case 'year':
        matchesTime = eventDate >= startOfYear && eventDate <= today
        break
      case 'all':
        matchesTime = true
        break
    }
    
    return matchesSearch && matchesTime
  })

  const formatDate = (dateString: string) => {
    if (!dateString) return 'TBD'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatTime = (timeString: string) => {
    if (!timeString) return 'TBD'
    const time = new Date(`2000-01-01T${timeString}`)
    return time.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const toggleEventExpansion = (eventId: number) => {
    const newExpanded = new Set(expandedEvents)
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId)
    } else {
      newExpanded.add(eventId)
    }
    setExpandedEvents(newExpanded)
  }



  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg text-gray-900 dark:text-gray-100">Loading events...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg text-red-600 dark:text-red-400">Error loading events: {error.message}</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Events</h1>
        <p className="text-gray-600 dark:text-gray-400">Discover and explore upcoming events</p>
      </div>
      
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <Input
            placeholder="Search events or clubs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
          />
          
          <Select value={timeFilter} onValueChange={setTimeFilter}>
            <SelectTrigger className="w-full sm:w-auto">
              <SelectValue placeholder="Filter by time" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="year">This Year</SelectItem>
              <SelectItem value="all">All Time</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing {filteredEvents.length} of {events.length} events
          </p>
        </div>
      </div>

      {/* Events Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(300px,_1fr))] gap-4 sm:gap-6">
        {filteredEvents.map((event, index) => {
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

      {filteredEvents.length === 0 && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">No events found</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">Try adjusting your search or filters</p>
          </div>
        </div>
      )}
    </div>
  )
} 