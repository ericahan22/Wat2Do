import { useRef, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { EVENT_EMOJIS_CATEGORIES } from "@/data/staticData";

// Use event categories directly

export const useQuickFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);

  const currentCategories = searchParams.get("categories") || "";

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
    (category: string) => {
      // Don't trigger click if user was dragging
      if (hasDragged) {
        return;
      }

      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        const currentCategoriesValue = nextParams.get("categories") || "";

        // Parse semicolon-separated categories
        const categories = currentCategoriesValue
          ? currentCategoriesValue
              .split(";")
              .map((c) => c.trim())
              .filter((c) => c)
          : [];

        // Check if category is already active (case-insensitive)
        const isActive = categories.some(
          (c) => c.toLowerCase() === category.toLowerCase()
        );

        if (isActive) {
          // Remove the category
          const updatedCategories = categories.filter(
            (c) => c.toLowerCase() !== category.toLowerCase()
          );

          if (updatedCategories.length > 0) {
            nextParams.set("categories", updatedCategories.join(";"));
          } else {
            nextParams.delete("categories");
          }
        } else {
          // Add the category
          categories.push(category);
          nextParams.set("categories", categories.join(";"));
        }

        return nextParams;
      });
    },
    [hasDragged, setSearchParams]
  );

  const isFilterActive = useCallback(
    (category: string) => {
      // Parse semicolon-separated categories and check if this category is active
      if (!currentCategories) return false;
      const categories = currentCategories
        .split(";")
        .map((c) => c.trim())
        .filter((c) => c);
      return categories.some((c) => c.toLowerCase() === category.toLowerCase());
    },
    [currentCategories]
  );

  return {
    // Data
    filterOptions: EVENT_EMOJIS_CATEGORIES,
    currentCategories,

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
