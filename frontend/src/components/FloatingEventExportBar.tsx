import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { SiApple } from "react-icons/si";
import { FcGoogle } from "react-icons/fc";
import { Event } from "@/hooks";

interface FloatingEventExportBarProps {
  view: "grid" | "calendar";
  isSelectMode: boolean;
  selectedEvents: Set<string>;
  onCancel: () => void;
  onExportICalendar: (events: Event[]) => void;
  onExportGoogleCalendar: (events: Event[]) => void;
  data: Event[];
}

export default function FloatingEventExportBar({
  view,
  isSelectMode,
  selectedEvents,
  onCancel,
  onExportICalendar,
  onExportGoogleCalendar,
  data,
}: FloatingEventExportBarProps) {
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
        <Button
          size="sm"
          onClick={() => onExportICalendar(data)}
          className="rounded-full"
          variant="default"
        >
          <SiApple className="h-4 w-4" />
          Export {selectedEvents.size} to iCalendar
        </Button>
        {selectedEvents.size === 1 && (
          <Button
            size="sm"
            onClick={() => onExportGoogleCalendar(data)}
            className="rounded-full"
            variant="default"
          >
            <FcGoogle className="h-4 w-4" />
            Export {selectedEvents.size} to Google Calendar
          </Button>
        )}
        <Button
          size="sm"
          onMouseDown={onCancel}
          className="rounded-full"
          variant="outline"
        >
          <X className="h-4 w-4" />
          Cancel
        </Button>
      </div>
    </div>
  );
}
