import React from "react";
import { Button } from "@/shared/components/ui/button";
import { X } from "lucide-react";
import { useQuickFilters } from "@/features/events/hooks/useQuickFilters";
import { getEmojiUrl, FilterWithEmoji } from "@/shared/lib/emojiUtils";

const QuickFilters: React.FC = () => {
  const {
    filterOptions,
    scrollContainerRef,
    handleMouseDown,
    handleFilterClick,
    handleFilterRemoveClick,
    isFilterActive,
  } = useQuickFilters();

  return (
    <div
      ref={scrollContainerRef}
      className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden select-none"
      style={{
        scrollbarWidth: "none",
        msOverflowStyle: "none",
        cursor: "grab",
      }}
      onMouseDown={handleMouseDown}
    >
      {filterOptions
        .sort((a, b) => {
          const aActive = isFilterActive(a);
          const bActive = isFilterActive(b);
          // Active filters first, then inactive ones
          if (aActive && !bActive) return -1;
          if (!aActive && bActive) return 1;
          return 0; // Maintain original order for same state
        })
        .map((filter) => {
          const isActive = isFilterActive(filter);
          const filterItem = filter as FilterWithEmoji;
          const emojiUrl = getEmojiUrl(filterItem);
          const filterName = filterItem[2];

          return (
            <Button
              key={filterName}
              variant="ghost"
              size="sm"
              className={`shrink-0 h-8 px-3 text-xs border rounded-full flex items-center gap-1 ${
                isActive
                  ? "bg-gray-700 border-gray-700 hover:bg-gray-600 hover:border-gray-600 dark:bg-gray-200 dark:border-gray-200 dark:hover:bg-gray-300 dark:hover:border-gray-300"
                  : "border-gray-100 bg-gray-100 hover:bg-gray-200 hover:border-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:border-gray-800 dark:hover:border-gray-700"
              }`}
              onClick={() => handleFilterClick(filter)}
            >
              {isActive && (
                <X
                  className={`h-3 w-3 ${
                    isActive ? "!text-gray-200 dark:!text-gray-800" : ""
                  }`}
                  onClick={handleFilterRemoveClick}
                />
              )}
              <img
                src={emojiUrl}
                alt={filterName}
                className="h-4 w-4 object-contain"
              />
              <span
                className={isActive ? "!text-gray-200 dark:!text-gray-800" : ""}
              >
                {filterName}
              </span>
            </Button>
          );
        })}
    </div>
  );
};

export default QuickFilters;
