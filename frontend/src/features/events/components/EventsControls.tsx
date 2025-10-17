import React from "react";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Button } from "@/shared/components/ui/button";
import { Calendar, LayoutGrid, X, History } from "lucide-react";

interface EventsControlsProps {
  view: "grid" | "calendar";
  isSelectMode: boolean;
  isShowingPastEvents: boolean;
  onViewChange: (view: "grid" | "calendar") => void;
  onToggleSelectMode: () => void;
  onToggleStartDate: () => void;
}

const EventsControls: React.FC<EventsControlsProps> = ({
  view,
  isSelectMode,
  isShowingPastEvents,
  onViewChange,
  onToggleSelectMode,
  onToggleStartDate,
}) => {

  return (
    <div className="flex justify-end ml-auto gap-2">
      {view === "grid" && (
        <Button
          variant="outline"
          size="default"
          className="h-9"
          onMouseDown={onToggleSelectMode}
        >
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
      
      <Button
        variant="outline"
        size="default"
        className="h-9"
        onMouseDown={onToggleStartDate}
      >
        <History className="h-4 w-4" />
        {isShowingPastEvents ? "Show Upcoming" : "Show Past Events"}
      </Button>
      
      <Tabs value={view} onValueChange={(value) => onViewChange(value as "grid" | "calendar")}>
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
  );
};

export default EventsControls;
