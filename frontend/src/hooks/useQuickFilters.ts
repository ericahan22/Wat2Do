import { useRef, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { RECOMMENDED_FILTERS } from "@/data/staticData";

// Fallback filters if none are generated yet
const FALLBACK_FILTERS = [
  "Bubble Tea",
  "Domino's Pizza",
  "Actuarial Science",
  "Free Food",
  "Computer Science",
  "Networking",
  "Engineering",
  "Business",
  "Math",
  "Coffee",
  "Workshop",
  "Career Fair",
  "Social",
  "Sports",
  "Music",
  "Art",
  "Gaming",
  "Hackathon",
  "Study Group",
];

// Use recommended filters if available, otherwise use fallback
const filterOptions = RECOMMENDED_FILTERS && RECOMMENDED_FILTERS.length > 0 
  ? RECOMMENDED_FILTERS 
  : FALLBACK_FILTERS;

export const useQuickFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);

  // Get current search term from URL
  const currentSearch = searchParams.get("search") || "";

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!scrollContainerRef.current) return;
    setIsDragging(true);
    setHasDragged(false);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
    scrollContainerRef.current.style.cursor = "grabbing";
  }, []);

  const handleMouseUp = useCallback(() => {
    if (!scrollContainerRef.current) return;
    setIsDragging(false);
    scrollContainerRef.current.style.cursor = "grab";
    // Reset hasDragged after a short delay to allow click event to check it
    setTimeout(() => setHasDragged(false), 100);
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !scrollContainerRef.current) return;
      e.preventDefault();
      const x = e.pageX - scrollContainerRef.current.offsetLeft;
      const walk = x - startX;
      
      // If moved more than 5 pixels, consider it a drag
      if (Math.abs(walk) > 5) {
        setHasDragged(true);
      }
      
      scrollContainerRef.current.scrollLeft = scrollLeft - walk;
    },
    [isDragging, startX, scrollLeft]
  );

  // Attach global mouse event listeners when dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const handleFilterClick = useCallback((filter: string) => {
    // Don't trigger click if user was dragging
    if (hasDragged) {
      return;
    }
    
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      const currentSearchValue = nextParams.get("search") || "";
      
      // Create a regex to find the filter as a complete phrase (case-insensitive)
      // Use word boundaries for single words, or exact phrase matching for multi-word
      const filterRegex = new RegExp(`(^|\\s)${filter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s|$)`, 'i');
      const isActive = filterRegex.test(currentSearchValue);
      
      if (isActive) {
        // Remove the filter from search (exact phrase match)
        const updatedSearch = currentSearchValue
          .replace(filterRegex, ' ')
          .replace(/\s+/g, ' ') // Replace multiple spaces with single space
          .trim();
        
        if (updatedSearch) {
          nextParams.set("search", updatedSearch);
        } else {
          nextParams.delete("search");
        }
      } else {
        // Add filter to existing search
        const newSearchValue = currentSearchValue 
          ? `${currentSearchValue} ${filter}` 
          : filter;
        nextParams.set("search", newSearchValue);
      }
      
      return nextParams;
    });
  }, [hasDragged, setSearchParams]);

  const handleFilterRemove = useCallback(() => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.delete("search");
      return nextParams;
    });
  }, [setSearchParams]);

  const isFilterActive = useCallback((filter: string) => {
    // Direct match: check if filter exists as a complete phrase in the search
    // Use word boundaries for single words, or exact phrase matching for multi-word
    const filterRegex = new RegExp(`(^|\\s)${filter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s|$)`, 'i');
    return filterRegex.test(currentSearch);
  }, [currentSearch]);

  const handleFilterRemoveClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the filter click
    handleFilterRemove();
  }, [handleFilterRemove]);

  return {
    // Data
    filterOptions,
    currentSearch,
    
    // Refs
    scrollContainerRef,
    
    // State
    isDragging,
    hasDragged,
    
    // Event handlers
    handleMouseDown,
    handleFilterClick,
    handleFilterRemoveClick,
    
    // Utilities
    isFilterActive,
  };
};
