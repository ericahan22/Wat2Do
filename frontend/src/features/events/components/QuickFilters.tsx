import React from "react";
import { Button } from "@/shared/components/ui/button";
import { useQuickFilters } from "@/features/events/hooks/useQuickFilters";
import { cn } from "@/shared/lib/utils";
import { getEmojiUrl } from "@/shared/lib/emojiUtils";

const QuickFilters: React.FC = () => {
  const {
    filterOptions,
    scrollContainerRef,
    handleMouseDown,
    handleFilterClick,
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
      {filterOptions.map(([emojiCategory, emoji, category]) => {
        const isActive = isFilterActive(category);

        return (
          <Button
            key={category}
            variant="ghost"
            size="sm"
            className={`shrink-0 h-8 px-3 text-xs border rounded-xl flex items-center gap-2 ${
              isActive
                ? "bg-gray-700 border-gray-700 hover:bg-gray-600 hover:border-gray-600 dark:bg-gray-200 dark:border-gray-200 dark:hover:bg-gray-300 dark:hover:border-gray-300"
                : "border-gray-100 bg-gray-100 hover:bg-gray-200 hover:border-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:border-gray-800 dark:hover:border-gray-700"
            }`}
            onClick={() => handleFilterClick(category)}
          >
            <img
              src={getEmojiUrl([emojiCategory, emoji])}
              alt={category}
              className="w-4 h-4"
            />
            <p
              className={cn(
                "text-sm",
                isActive ? "!text-gray-200 dark:!text-gray-800" : ""
              )}
            >
              {category}
            </p>
          </Button>
        );
      })}
    </div>
  );
};

export default QuickFilters;
