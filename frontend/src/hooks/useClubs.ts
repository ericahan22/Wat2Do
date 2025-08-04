import { useState, useMemo, useEffect } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { useInView } from 'react-intersection-observer'

export interface Club {
  id: number
  club_name: string
  categories: string[]
  club_page: string
  ig: string
  discord: string
}

interface ClubsResponse {
  clubs: Club[]
  count: number
  total_count: number
  has_more: boolean
  next_offset: number | null
  current_offset: number
  limit: number
}

const fetchClubs = async ({ pageParam = 0 }): Promise<ClubsResponse> => {
  const response = await fetch(`http://localhost:8000/api/clubs/?limit=20&offset=${pageParam}`)
  if (!response.ok) {
    throw new Error('Failed to fetch clubs')
  }
  const data: ClubsResponse = await response.json()
  return data
}

export function useClubs() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ['clubs'],
    queryFn: fetchClubs,
    getNextPageParam: (lastPage) => lastPage.has_more ? lastPage.next_offset : undefined,
    initialPageParam: 0,
  })

  // Flatten all pages into a single array of clubs
  const allClubs = useMemo(() => {
    return data?.pages.flatMap(page => page.clubs) || []
  }, [data])

  const filteredClubs = useMemo(() => {
    return allClubs.filter((club: Club) => {
      const matchesSearch = !searchTerm || 
        club.club_name.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesCategory = categoryFilter === 'all' || 
        club.categories.some(category => 
          category.toLowerCase().includes(categoryFilter.toLowerCase())
        )
      
      return matchesSearch && matchesCategory
    })
  }, [allClubs, searchTerm, categoryFilter])

  const uniqueCategories = useMemo(() => {
    return [...new Set(
      allClubs.flatMap((club: Club) => club.categories || [])
    )].sort()
  }, [allClubs])

  // Intersection observer for infinite scrolling
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '100px',
  })

  // Fetch next page when the element comes into view
  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage()
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage])

  return {
    // Data
    allClubs,
    filteredClubs,
    uniqueCategories,
    
    // State
    searchTerm,
    setSearchTerm,
    categoryFilter,
    setCategoryFilter,
    
    // Query state
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    
    // Infinite scrolling
    infiniteScrollRef: ref,
    
    // Metadata
    totalCount: data?.pages[0]?.total_count,
  }
}