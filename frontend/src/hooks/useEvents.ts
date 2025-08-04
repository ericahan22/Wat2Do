import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

export interface Event {
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

export function useEvents() {
  const [searchTerm, setSearchTerm] = useState('')
  const [timeFilter, setTimeFilter] = useState('today')
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set())

  const { data: events = [], isLoading, error } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents,
  })

  const filteredEvents = useMemo(() => {
    return events.filter((event: Event) => {
      const matchesSearch = !searchTerm || 
        event.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.club_handle.toLowerCase().includes(searchTerm.toLowerCase())
      
      // Time-based filtering
      if (!event.date) return matchesSearch
      
      const eventDate = new Date(event.date)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      // Calculate time period boundaries
      const startOfWeek = new Date(today)
      startOfWeek.setDate(today.getDate() - today.getDay())
      const endOfWeek = new Date(startOfWeek)
      endOfWeek.setDate(startOfWeek.getDate() + 6)
      endOfWeek.setHours(23, 59, 59, 999)
      
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      endOfMonth.setHours(23, 59, 59, 999)
      
      const startOfYear = new Date(today.getFullYear(), 0, 1)
      const endOfYear = new Date(today.getFullYear(), 11, 31)
      endOfYear.setHours(23, 59, 59, 999)
      
      const endOfToday = new Date(today)
      endOfToday.setHours(23, 59, 59, 999)
      
      let matchesTime = true
      switch (timeFilter) {
        case 'today':
          matchesTime = eventDate >= today && eventDate <= endOfToday
          break
        case 'week':
          matchesTime = eventDate >= startOfWeek && eventDate <= endOfWeek
          break
        case 'month':
          matchesTime = eventDate >= startOfMonth && eventDate <= endOfMonth
          break
        case 'year':
          matchesTime = eventDate >= startOfYear && eventDate <= endOfYear
          break
        case 'all':
          matchesTime = true
          break
      }
      
      return matchesSearch && matchesTime
    })
  }, [events, searchTerm, timeFilter])

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

  return {
    // Data
    events,
    filteredEvents,
    
    // State
    searchTerm,
    setSearchTerm,
    timeFilter,
    setTimeFilter,
    expandedEvents,
    
    // Query state
    isLoading,
    error,
    
    // Utility functions
    formatDate,
    formatTime,
    toggleEventExpansion,
  }
}