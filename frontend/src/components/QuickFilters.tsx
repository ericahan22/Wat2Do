import React from "react";
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
  const handleFilterClick = (filter: string) => {
    if (onFilterClick) {
      onFilterClick(filter);
    }
  };

  return (
    <div className="relative w-full">
      <div 
        className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden"
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
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

