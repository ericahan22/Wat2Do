import { Button } from "@/shared/components/ui/button";
import { X } from "lucide-react";
import { SiApple } from "react-icons/si";
import { FcGoogle } from "react-icons/fc";

interface FloatingEventExportBarProps {
  view: "grid" | "calendar";
  isSelectMode: boolean;
  selectedEvents: Set<string>;
  onCancel: () => void;
  onExportICalendar: () => void;
  onExportGoogleCalendar: () => void;
}

export default function FloatingEventExportBar({
  view,
  isSelectMode,
  selectedEvents,
  onCancel,
  onExportICalendar,
  onExportGoogleCalendar,
}: FloatingEventExportBarProps) {
  return (
    <div
      className={
        `fixed bottom-6 left-1/2 -translate-x-1/2 z-50 transform-gpu max-w-screen` +
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
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md rounded-4xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 px-3 py-3 sm:flex-row flex-col flex items-center gap-4">
        {selectedEvents.size > 0 && (
          <>
            <Button
              onClick={onExportICalendar}
              className="rounded-full w-full"
              variant="ghost"
            >
              <SiApple className="h-4 w-4" />
              Export {selectedEvents.size} to Calendar
            </Button>
            <Button
              onClick={onExportGoogleCalendar}
              className="rounded-full w-full"
              variant="ghost"
            >
              <FcGoogle className="h-4 w-4" />
              Export {selectedEvents.size} to Google Calendar
            </Button>
          </>
        )}
        <Button
          onMouseDown={onCancel}
          className="rounded-full w-full"
          variant="ghost"
        >
          <X className="h-4 w-4" />
          Cancel
        </Button>
      </div>
    </div>
  );
}
