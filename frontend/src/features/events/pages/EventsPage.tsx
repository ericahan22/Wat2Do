import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  useEvents,
  useEventSelection,
  EventsContent,
  QuickFilters,
} from "@/features/events";
import {
  getTodayString,
  SEOHead,
  Tabs,
  TabsList,
  TabsTrigger,
  FloatingEventExportBar,
  formatRelativeDateTime,
  FilterButton,
  // JSONEditor,
} from "@/shared";
import { Calendar, LayoutGrid, Sparkles, Heart, Clock } from "lucide-react";
import SearchInput from "@/features/search/components/SearchInput";
import NumberFlow from "@number-flow/react";
import { LAST_UPDATED, EVENT_CATEGORIES } from "@/data/staticData";

function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";
  const randomCategory = useMemo(
    () => EVENT_CATEGORIES[Math.floor(Math.random() * EVENT_CATEGORIES.length)],
    []
  );
  const placeholder = searchParams.get("placeholder") || randomCategory;

  const handleViewChange = useCallback(
    (newView: "grid" | "calendar") => {
      const newParams = new URLSearchParams(searchParams);
      newParams.set("view", newView);
      setSearchParams(newParams);
    },
    [searchParams, setSearchParams]
  );

  const {
    events,
    totalCount,
    isLoading,
    error,
    dtstart_utc,
    addedAt,
    showInterested,
    searchTerm,
    categories,
    handleToggleNewEvents,
    handleToggleInterested,
    handleToggleAllEvents,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useEvents();

  const {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
  } = useEventSelection(view);

  const todayString = getTodayString();
  const isShowingPastEvents = Boolean(
    dtstart_utc && dtstart_utc !== todayString
  );
  const isShowingNewEvents = Boolean(addedAt);
  const isShowingAllEvents = Boolean(dtstart_utc);

  const getEventTypeText = () => {
    if (searchTerm || categories) return "Found";
    if (showInterested) return "Interested";
    if (addedAt) return "New";
    if (isShowingPastEvents) return "Total";
    return "Upcoming";
  };

  // Use totalCount when available, except for interested filter which filters client-side
  const displayCount = showInterested
    ? events.length
    : totalCount || events.length;

  return (
    <>
      <SEOHead
        title="Events - Discover University of Waterloo Club Events"
        description="Browse and discover exciting club events at the University of Waterloo. Find upcoming events, filter by date, and stay connected with campus activities."
        url="/events"
        keywords={[
          "University of Waterloo events",
          "UW club events",
          "campus events",
          "student events",
          "Waterloo university events",
          "upcoming events",
          "event calendar",
          "campus activities",
        ]}
      />
      {/* <JSONEditor /> */}
      <div className="flex flex-col gap-4">
        <div className="sm:text-left">
          <h1 className="sm:text-3xl text-2xl font-bold mb-2 -mt-3 sm:mt-0">
            <NumberFlow
              value={displayCount}
              suffix={` ${getEventTypeText()} events`}
            />
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Updated {formatRelativeDateTime(LAST_UPDATED)}
          </p>
        </div>

        <div className="flex flex-col sm:gap-4 gap-3.5">
          <div className="flex items-center sm:gap-4 gap-2">
            <SearchInput placeholder={placeholder} className="flex-1" />
            <Tabs
              value={view}
              onValueChange={(value) =>
                handleViewChange(value as "grid" | "calendar")
              }
            >
              <TabsList>
                <TabsTrigger value="grid" className="flex items-center gap-2">
                  <LayoutGrid className="h-4 w-4" />
                  Grid
                </TabsTrigger>
                <TabsTrigger
                  value="calendar"
                  className="flex items-center gap-2"
                >
                  <Calendar className="h-4 w-4" />
                  Calendar
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          <QuickFilters />

          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <FilterButton
                isActive={isShowingNewEvents}
                onToggle={handleToggleNewEvents}
                icon={<Sparkles className="h-4 w-4" />}
              >
                Newly Added
              </FilterButton>
              <FilterButton
                isActive={isShowingAllEvents}
                onToggle={handleToggleAllEvents}
                icon={<Clock className="h-4 w-4" />}
              >
                All
              </FilterButton>
              <FilterButton
                isActive={showInterested}
                onToggle={handleToggleInterested}
                icon={<Heart className="h-4 w-4" />}
              >
                Interested
              </FilterButton>
              {view === "grid" && (
                <FilterButton
                  isActive={isSelectMode}
                  onToggle={toggleSelectMode}
                  icon={<Calendar className="h-4 w-4" />}
                >
                  Export
                </FilterButton>
              )}
            </div>
          </div>
        </div>

        <EventsContent
          view={view}
          data={events}
          isSelectMode={isSelectMode}
          selectedEvents={selectedEvents}
          onToggleEvent={toggleEventSelection}
          isLoading={isLoading}
          error={error}
          fetchNextPage={fetchNextPage}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
        />

        <FloatingEventExportBar
          view={view}
          isSelectMode={isSelectMode}
          selectedEvents={selectedEvents}
          onCancel={toggleSelectMode}
          onExportICalendar={exportToCalendar}
          onExportGoogleCalendar={exportToGoogleCalendar}
        />
      </div>
    </>
  );
}

export default EventsPage;
