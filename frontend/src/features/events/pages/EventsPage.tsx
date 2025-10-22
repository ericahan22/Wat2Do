import { useCallback, memo } from "react";
import { useSearchParams } from "react-router-dom";
import { useEvents } from "@/features/events/hooks/useEvents";
import { useEventSelection } from "@/features/events/hooks/useEventSelection";
import { getTodayString } from "@/shared/lib/dateUtils";
import { SEOHead } from "@/shared/components/SEOHead";
import { Button } from "@/shared/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Calendar, X, History, LayoutGrid, Sparkles } from "lucide-react";

// Components
import EventsHeader from "@/features/events/components/EventsHeader";
import EventsStatusBar from "@/features/events/components/EventsStatusBar";
import EventsContent from "@/features/events/components/EventsContent";
import SearchInput from "@/features/search/components/SearchInput";
import QuickFilters from "@/features/events/components/QuickFilters";
import FloatingEventExportBar from "@/shared/components/common/FloatingEventExportBar";

function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";

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
    searchTerm,
    dtstart,
    addedAt,
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
  const isShowingPastEvents = Boolean(dtstart && dtstart !== todayString);
  const isShowingNewEvents = Boolean(addedAt);

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
      <EventsHeader />

      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <SearchInput placeholder="Filter events by..." className="flex-1" />
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
          <EventsStatusBar
            isLoading={isLoading}
            searchTerm={searchTerm}
            isShowingPastEvents={isShowingPastEvents}
            totalCount={data.length}
          />
          <div className="flex">
            <Button variant="ghost" onMouseDown={handleToggleNewEvents}>
              <Sparkles className="h-4 w-4" />
              {isShowingNewEvents ? "All" : "New"}
            </Button>
            <Button variant="ghost" onMouseDown={handleToggleStartDate}>
              <History className="h-4 w-4" />
              {isShowingPastEvents ? "Upcoming" : "Past"}
            </Button>
            {view === "grid" && (
              <Button variant="ghost" onMouseDown={toggleSelectMode}>
                {isSelectMode ? (
                  <>
                    <X className="h-4 w-4" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Calendar className="h-4 w-4" />
                    Export
                  </>
                )}
              </Button>
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

export default memo(EventsPage);
