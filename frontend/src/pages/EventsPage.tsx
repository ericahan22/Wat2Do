import React, { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar, LayoutGrid } from "lucide-react";
import { useEvents } from "@/hooks";
import { useCategoryParam } from "@/hooks/useCategoryParam";
import EventsGrid from "@/components/EventsGrid";
import EventsCalendar from "@/components/EventsCalendar";
import SearchInput from "@/components/SearchInput";


function EventsPage() {
  const [view, setView] = useState<"grid" | "calendar">("calendar"); // to toggle views

  const {
    data,
    uniqueCategories,
    isLoading,
    error,
  } = useEvents(view);

  const { categoryParam, setCategoryParam } = useCategoryParam();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Events
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover and explore upcoming events
        </p>
      </div>

      {/* Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput placeholder="Search events..." className="flex-1" />

          <Select value={categoryParam} onValueChange={setCategoryParam}>
            <SelectTrigger className="w-full sm:w-auto">
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {uniqueCategories.map((category: string) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* button to toggle between views */}
          <div className="flex space-x-0 border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden">
              <div
                onMouseDown={() => setView("calendar")}
                className={`flex items-center justify-center w-9 h-full
                  ${
                    view === "calendar"
                      ? "bg-gray-200 dark:bg-gray-700"
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  }
                  focus:outline-none focus:ring-2 focus:ring-gray-300 dark:focus:ring-gray-500`}
                title="Calendar View"
                aria-label="Calendar View"
              >
                <Calendar className="h-5 w-5 text-gray-800 dark:text-gray-200" />
              </div>
            <div
              onMouseDown={() => setView("grid")}
              className={`flex items-center justify-center w-9 h-full border-r border-gray-300 dark:border-gray-600
                ${
                  view === "grid"
                    ? "bg-gray-200 dark:bg-gray-700"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                }
                focus:outline-none focus:ring-2 focus:ring-gray-300 dark:focus:ring-gray-500`}
              title="Grid View"
              aria-label="Grid View"
            >
              <LayoutGrid className="h-5 w-5 text-gray-800 dark:text-gray-200" />
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLoading ? "Loading..." : view === "grid" ? `Showing ${data.length} upcoming events` : `Showing ${data.length} events`}
          </p>
        </div>
      </div>

      {/* Loading state - show content with loading indicator */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <span>Loading events...</span>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex items-center justify-center py-8">
          <div className="text-lg text-red-600 dark:text-red-400">
            Error loading events: {error.message}
          </div>
        </div>
      )}

      {/* Render appropriate view */}
      {!isLoading && !error && (
        <>
          {view === "grid" ? (
            <EventsGrid data={data} />
          ) : (
            <EventsCalendar
              events={data.map((event) => ({
                ...event,
                id: String(event.id),
              }))}
            />
          )}
        </>
      )}
    </div>
  );
}

export default React.memo(EventsPage);
