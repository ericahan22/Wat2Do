import { Button } from "@/components/ui/button";
import { Calendar, X } from "lucide-react";
import { Event } from "@/hooks";

interface FloatingExportBarProps {
  view: "grid" | "calendar";
  isSelectMode: boolean;
  selectedEvents: Set<string>;
  onCancel: () => void;
  onExport: (events: Event[]) => void;
  data: Event[];
}

export default function FloatingExportBar({
  view,
  isSelectMode,
  selectedEvents,
  onCancel,
  onExport,
  data,
}: FloatingExportBarProps) {
  return (
    <div
      className={
        `fixed bottom-6 left-1/2 -translate-x-1/2 z-50 transform-gpu ` +
        `transition-all duration-300 ease-out ` +
        `${
          view === "grid" && isSelectMode && selectedEvents.size > 0
            ? "opacity-100 translate-y-0 scale-100"
            : "pointer-events-none opacity-0 translate-y-2 scale-95"
        }`
      }
      aria-hidden={
        view !== "grid" || !isSelectMode || selectedEvents.size === 0
      }
    >
      <div className="bg-white dark:bg-gray-800 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center gap-4">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {selectedEvents.size} event{selectedEvents.size !== 1 ? "s" : ""}{" "}
          selected
        </span>
        <Button
          size="sm"
          onClick={() => onExport(data)}
          className="rounded-full"
        >
          <Calendar className="h-4 w-4" />
          Export to iCalendar
        </Button>
        <Button
          size="sm"
          onMouseDown={onCancel}
          className="rounded-full"
        >
          <X className="h-4 w-4" />
          Cancel
        </Button>
      </div>
    </div>
  );
}
