import { useRef, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { RECOMMENDED_FILTERS } from "@/data/staticData";
import { FilterWithEmoji } from "@/shared/lib/emojiUtils";

// Use recommended filters directly

export const useQuickFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);

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
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);

      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const handleFilterClick = useCallback(
    (filter: FilterWithEmoji) => {
      // Don't trigger click if user was dragging
      if (hasDragged) {
        return;
      }

      const filterName = filter[2]; // Extract filter name from 3D array

      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        const currentSearchValue = nextParams.get("search") || "";

        // Parse semicolon-separated filters
        const filters = currentSearchValue
          ? currentSearchValue.split(";").map((f) => f.trim()).filter((f) => f)
          : [];

        // Check if filter is already active (case-insensitive)
        const isActive = filters.some(
          (f) => f.toLowerCase() === filterName.toLowerCase()
        );

        if (isActive) {
          // Remove the filter
          const updatedFilters = filters.filter(
            (f) => f.toLowerCase() !== filterName.toLowerCase()
          );

          if (updatedFilters.length > 0) {
            nextParams.set("search", updatedFilters.join(";"));
          } else {
            nextParams.delete("search");
          }
        } else {
          // Add the filter
          filters.push(filterName);
          nextParams.set("search", filters.join(";"));
        }

        return nextParams;
      });
    },
    [hasDragged, setSearchParams]
  );

  const isFilterActive = useCallback(
    (filter: FilterWithEmoji) => {
      const filterName = filter[2];
      // Parse semicolon-separated filters and check if this filter is active
      if (!currentSearch) return false;
      const filters = currentSearch
        .split(";")
        .map((f) => f.trim())
        .filter((f) => f);
      return filters.some(
        (f) => f.toLowerCase() === filterName.toLowerCase()
      );
    },
    [currentSearch]
  );

  return {
    // Data
    filterOptions: RECOMMENDED_FILTERS,
    currentSearch,

    // Refs
    scrollContainerRef,

    // State
    isDragging,
    hasDragged,

    // Event handlers
    handleMouseDown,
    handleFilterClick,

    // Utilities
    isFilterActive,
  };
};
