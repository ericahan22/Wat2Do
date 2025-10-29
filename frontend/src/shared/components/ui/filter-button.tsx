import React from "react";
import { Button } from "./button";
import { cn } from "@/shared/lib/utils";

interface FilterButtonProps {
  isActive: boolean;
  onToggle: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const FilterButton: React.FC<FilterButtonProps> = ({
  isActive,
  onToggle,
  icon,
  children,
  className,
}) => {
  return (
    <Button
      variant="ghost"
      onMouseDown={onToggle}
      className={cn(
        "shrink-0 h-8 px-3 text-xs border rounded-xl flex items-center gap-2",
        isActive
          ? "bg-gray-700 border-gray-700 hover:bg-gray-600 hover:border-gray-600 dark:bg-gray-200 dark:border-gray-200 dark:hover:bg-gray-300 dark:hover:border-gray-300"
          : "border-gray-100 bg-gray-100 hover:bg-gray-200 hover:border-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:border-gray-800 dark:hover:border-gray-700",
        className
      )}
    >
      <div
        className={cn(
          "h-4 w-4",
          isActive ? "!text-gray-200 dark:!text-gray-800" : ""
        )}
      >
        {icon}
      </div>
      <p
        className={cn(
          "text-sm",
          isActive ? "!text-gray-200 dark:!text-gray-800" : ""
        )}
      >
        {children}
      </p>
    </Button>
  );
};
