import { useCallback, memo } from "react";
import { useSearchParams } from "react-router-dom";
import { useEvents } from "@/features/events/hooks/useEvents";
import { useEventSelection } from "@/features/events/hooks/useEventSelection";
import { getTodayString } from "@/shared/lib/dateUtils";

// Components
import EventsHeader from "@/features/events/components/EventsHeader";
import EventsControls from "@/features/events/components/EventsControls";
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
    handleToggleStartDate,
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

  return (
    <div className="flex flex-col gap-4">
      <EventsHeader />

      <div className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row gap-4">
          <SearchInput placeholder="Filter events by..." className="flex-1" />
          <EventsControls
            view={view}
            isSelectMode={isSelectMode}
            isShowingPastEvents={isShowingPastEvents}
            onViewChange={handleViewChange}
            onToggleSelectMode={toggleSelectMode}
            onToggleStartDate={handleToggleStartDate}
          />
        </div>

        <QuickFilters />

        <EventsStatusBar
          isLoading={isLoading}
          searchTerm={searchTerm}
          isShowingPastEvents={isShowingPastEvents}
          totalCount={data.length}
        />
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
