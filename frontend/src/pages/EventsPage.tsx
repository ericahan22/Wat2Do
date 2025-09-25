import React, { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, LayoutGrid } from "lucide-react";
import { useEvents } from "@/hooks";
import { useCategoryParam } from "@/hooks/useCategoryParam";
import EventsGrid from "@/components/EventsGrid";
import EventsCalendar from "@/components/EventsCalendar";
import EventLegend from "@/components/EventLegend";
import SearchInput from "@/components/SearchInput";

function EventsPage() {
  const [view, setView] = useState<"grid" | "calendar">("grid");

  const { data, uniqueCategories, isLoading, error } = useEvents(view);

  const { categoryParam, setCategoryParam } = useCategoryParam();

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Events
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover and explore upcoming events. Updates daily at 7am EST.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4">
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

          {/* View toggle tabs */}
          <Tabs
            value={view}
            onValueChange={(value) => setView(value as "grid" | "calendar")}
          >
            <TabsList>
              <TabsTrigger value="calendar" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Calendar
              </TabsTrigger>
              <TabsTrigger value="grid" className="flex items-center gap-2">
                <LayoutGrid className="h-4 w-4" />
                Grid
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLoading
              ? "Loading..."
              : view === "grid"
              ? `Showing ${data.length} upcoming events`
              : `Showing ${data.length} events`}
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
            <>
              <EventsCalendar events={data} />
              <EventLegend />
            </>
          )}
        </>
      )}
    </div>
  );
}

export default React.memo(EventsPage);
