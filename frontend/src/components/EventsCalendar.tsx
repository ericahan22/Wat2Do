import React, { useRef, useState } from "react";
import {
  Calendar,
  dateFnsLocalizer,
  NavigateAction,
  View,
} from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { enUS } from "date-fns/locale/en-US";
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  ExternalLink,
} from "lucide-react";
import "../styles/calendar.css";
import { formatTimeRange } from "@/lib/dateUtils";

const locales = {
  "en-US": enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface Event {
  id: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  club_handle: string;
  url?: string;
}

interface EventsCalendarProps {
  events: Event[];
}

// Custom toolbar for < and > month buttons
const CustomToolbar: React.FC<{
  label: string;
  onNavigate: (action: "PREV" | "NEXT" | "TODAY") => void;
}> = ({ label, onNavigate }) => {
  return (
    <div className="relative mb-4">
      {/* Today button */}
      <button
        onMouseDown={() => onNavigate("TODAY")}
        className="absolute left-0 top-1/2 -translate-y-1/2 rbc-btn px-4 py-1 text-sm font-medium text-gray-800 dark:text-gray-200 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
        aria-label="Today"
      >
        Today
      </button>

      <div className="flex items-center justify-center gap-4">
        {/* Back button < */}
        <button
          onMouseDown={() => onNavigate("PREV")}
          className="text-gray-800 dark:text-gray-200"
          aria-label="Previous Month"
          style={{ padding: "4px 8px" }}
        >
          <ChevronLeft className="h-6 w-6" />
        </button>

        {/* Month Year title */}
        <div
          className="flex items-center justify-center"
          style={{ width: "140px" }}
        >
          <h2 className="text-lg whitespace-nowrap font-bold text-gray-900 dark:text-white">
            {label}
          </h2>
        </div>

        {/* Next button > */}
        <button
          onMouseDown={() => onNavigate("NEXT")}
          className="text-gray-800 dark:text-gray-200"
          aria-label="Next Month"
          style={{ padding: "4px 8px" }}
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>
    </div>
  );
};

const EventsCalendar: React.FC<EventsCalendarProps> = ({ events }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [popupPosition, setPopupPosition] = useState<{
    x: number;
    y: number;
  } | null>(null);

  const calendarContainerRef = useRef<HTMLDivElement>(null);

  const calendarEvents = events.map((event) => ({
    ...event,
    title: event.name,
    start: new Date(`${event.date}T${event.start_time}`),
    end: new Date(`${event.date}T${event.end_time}`),
  }));

  const handleNavigate = (
    newDate: Date,
    _view: View,
    _action: NavigateAction
  ) => {
    setCurrentDate(newDate);
  };

  const handleSelectEvent = (
    event: typeof calendarEvents[number],
    e: React.SyntheticEvent<HTMLElement>
  ) => {
    e.stopPropagation();

    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const container = calendarContainerRef.current;
    if (!container) return;
    const containerRect = container.getBoundingClientRect();

    const popupWidth = 320;
    const popupHeight = 200;
    let x = rect.left - containerRect.left + rect.width + 10;
    let y = rect.top - containerRect.top;

    // Handle overflow
    if (x + popupWidth > containerRect.width) {
      x = rect.left - containerRect.left - popupWidth - 10;
    }
    if (y + popupHeight > containerRect.height) {
      y = containerRect.height - popupHeight - 10;
    }

    setSelectedEvent(event);
    setPopupPosition({ x, y });
  };

  const closePopup = () => {
    setSelectedEvent(null);
    setPopupPosition(null);
  };

  const handleOutsideClick = (e: React.MouseEvent) => {
    const popup = document.querySelector(".event-popup") as HTMLElement;
    const target = e.target as HTMLElement;

    if ((popup && popup.contains(target)) || target.closest(".rbc-event")) {
      return;
    }
    setSelectedEvent(null);
    setPopupPosition(null);
  };

  return (
    <div
      ref={calendarContainerRef}
      className="events-calendar-container relative"
      onMouseDown={handleOutsideClick}
    >
      <Calendar
        localizer={localizer}
        events={calendarEvents}
        startAccessor="start"
        endAccessor="end"
        date={currentDate}
        onNavigate={handleNavigate}
        selectable={false}
        onSelectSlot={() => {}}
        onSelectEvent={handleSelectEvent}
        components={{
          toolbar: CustomToolbar,
        }}
      />

      {/* Event details popup */}
      {selectedEvent && popupPosition && (
        <div
          className="event-popup absolute bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 w-80 z-50"
          style={{
            top: popupPosition.y,
            left: popupPosition.x,
          }}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onMouseDown={closePopup}
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
          >
            ✕
          </button>

          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-1 pr-8">
            {selectedEvent.name}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            @{selectedEvent.club_handle}
          </p>

          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
            <CalendarIcon className="h-4 w-4 flex-shrink-0" />
            <span>{format(new Date(selectedEvent.date), "MMMM dd, yyyy")}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
            <Clock className="h-4 w-4 flex-shrink-0" />
            <span>
              {formatTimeRange(selectedEvent.start_time, selectedEvent.end_time)}
            </span>
          </div>
          {selectedEvent.location && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
              <MapPin className="h-4 w-4 flex-shrink-0" />
              <span className="truncate" title={selectedEvent.location}>
                {selectedEvent.location}
              </span>
            </div>
          )}
          {selectedEvent.url && (
            <a
              href={selectedEvent.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-blue-500 hover:underline text-sm"
              title={selectedEvent.url}
            >
              <ExternalLink className="h-4 w-4 flex-shrink-0" />
              Event Link
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default EventsCalendar;
