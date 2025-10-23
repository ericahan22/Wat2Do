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

        // Use word boundaries for single words, or exact phrase matching for multi-word
        const filterRegex = new RegExp(
          `(^|\\s)${filterName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(\\s|$)`,
          "i"
        );
        const isActive = filterRegex.test(currentSearchValue);

        if (isActive) {
          const updatedSearch = currentSearchValue
            .replace(filterRegex, " ")
            .replace(/\s+/g, " ") // Replace multiple spaces with single space
            .trim();

          if (updatedSearch) {
            nextParams.set("search", updatedSearch);
          } else {
            nextParams.delete("search");
          }
        } else {
          const newSearchValue = currentSearchValue
            ? `${currentSearchValue} ${filterName}`
            : filterName;
          nextParams.set("search", newSearchValue);
        }

        return nextParams;
      });
    },
    [hasDragged, setSearchParams]
  );

  const handleFilterRemove = useCallback(() => {
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.delete("search");
      return nextParams;
    });
  }, [setSearchParams]);

  const isFilterActive = useCallback(
    (filter: FilterWithEmoji) => {
      const filterName = filter[2]; // Extract filter name from 3D array
      // Direct match: check if filter exists as a complete phrase in the search
      // Use word boundaries for single words, or exact phrase matching for multi-word
      const filterRegex = new RegExp(
        `(^|\\s)${filterName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(\\s|$)`,
        "i"
      );
      return filterRegex.test(currentSearch);
    },
    [currentSearch]
  );

  const handleFilterRemoveClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation(); // Prevent triggering the filter click
      handleFilterRemove();
    },
    [handleFilterRemove]
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
    handleFilterRemoveClick,

    // Utilities
    isFilterActive,
  };
};
