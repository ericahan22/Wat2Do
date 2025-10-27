import { useCallback } from "react";
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
} from "@/shared";
import { Calendar, History, LayoutGrid, Sparkles } from "lucide-react";
import SearchInput from "@/features/search/components/SearchInput";
import NumberFlow from "@number-flow/react";
import { LAST_UPDATED } from "@/data/staticData";

function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";
  const placeholder = searchParams.get("placeholder") || "Free food";

  const handleViewChange = useCallback(
    (newView: "grid" | "calendar") => {
      const newParams = new URLSearchParams(searchParams);
      newParams.set("view", newView);
      setSearchParams(newParams);
    },
    [searchParams, setSearchParams]
  );

  const {
    data,
    isLoading,
    error,
    dtstart_utc,
    addedAt,
    searchTerm,
    handleToggleStartDate,
    handleToggleNewEvents,
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
  const isShowingPastEvents = Boolean(dtstart_utc && dtstart_utc !== todayString);
  const isShowingNewEvents = Boolean(addedAt);

  const getEventTypeText = () => {
    if (searchTerm) return "Found";
    if (addedAt) return "New";
    if (isShowingPastEvents) return "Past";
    return "Upcoming";
  };

  return (
    <div className="flex flex-col gap-4">
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
      <div className="sm:text-left">
        <h1 className="sm:text-3xl text-2xl font-bold mb-2">
          <NumberFlow
            value={data.length}
            suffix={` ${getEventTypeText()} events`}
          />
        </h1>
        <p>Updated {formatRelativeDateTime(LAST_UPDATED)}</p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
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
              <TabsTrigger value="calendar" className="flex items-center gap-2">
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
            {!isShowingNewEvents && (
              <FilterButton
                isActive={isShowingPastEvents}
                onToggle={handleToggleStartDate}
                icon={<History className="h-4 w-4" />}
              >
                Past
              </FilterButton>
            )}
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
        data={data}
        isSelectMode={isSelectMode}
        selectedEvents={selectedEvents}
        onToggleEvent={toggleEventSelection}
        isLoading={isLoading}
        error={error}
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
  );
}

export default EventsPage;
