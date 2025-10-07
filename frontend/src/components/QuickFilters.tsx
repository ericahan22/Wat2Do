import React, { useRef, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";

const filterOptions = [
  "Bubble Tea",
  "Domino's Pizza",
  "Actuarial Science",
  "Free Food",
  "Computer Science",
  "Networking",
  "Engineering",
  "Business",
  "Math",
  "Pizza",
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

interface QuickFiltersProps {
  onFilterClick?: (filter: string) => void;
}

const QuickFilters: React.FC<QuickFiltersProps> = ({ onFilterClick }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!scrollContainerRef.current) return;
    setIsDragging(true);
    setHasDragged(false);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
    scrollContainerRef.current.style.cursor = "grabbing";
  }, []);

  const handleMouseLeave = useCallback(() => {
    if (!scrollContainerRef.current) return;
    setIsDragging(false);
    scrollContainerRef.current.style.cursor = "grab";
  }, []);

  const handleMouseUp = useCallback(() => {
    if (!scrollContainerRef.current) return;
    setIsDragging(false);
    scrollContainerRef.current.style.cursor = "grab";
    // Reset hasDragged after a short delay to allow click event to check it
    setTimeout(() => setHasDragged(false), 100);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
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

  const handleFilterClick = (filter: string) => {
    // Don't trigger click if user was dragging
    if (hasDragged) {
      return;
    }
    if (onFilterClick) {
      onFilterClick(filter);
    }
  };

  return (
    <div className="relative w-full">
      <div
        ref={scrollContainerRef}
        className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden select-none"
        style={{
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          cursor: "grab",
        }}
        onMouseDown={handleMouseDown}
        onMouseLeave={handleMouseLeave}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
      >
        {filterOptions.map((filter) => (
          <Button
            key={filter}
            variant="ghost"
            size="sm"
            className="shrink-0 h-8 px-3 text-xs border border-gray-100 bg-gray-100 hover:bg-gray-200 hover:border-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:border-gray-800 dark:hover:border-gray-700 rounded-full"
            onClick={() => handleFilterClick(filter)}
          >
            {filter}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default QuickFilters;
