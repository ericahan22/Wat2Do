import React, { useRef, useState, useEffect } from "react";
import {
  Calendar,
  dateFnsLocalizer,
  View,
  ToolbarProps,
} from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { enUS } from "date-fns/locale/en-US";
import { useLocalStorage } from "react-use";
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  ExternalLink,
  Utensils,
  DollarSign,
} from "lucide-react";
import "@/shared/styles/calendar.css";
import { formatTimeRange, formatEventDate } from "@/shared/lib/dateUtils";
import { getClubTypeColor } from "@/shared/lib/clubTypeColors";
import { Event } from "@/features/events";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { IconButton } from "@/shared/components/ui/icon-button";

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

const abbreviateLabel = (label: string): string => {
  const monthAbbreviations: Record<string, string> = {
    January: "Jan",
    February: "Feb",
    March: "Mar",
    April: "Apr",
    May: "May",
    June: "Jun",
    July: "Jul",
    August: "Aug",
    September: "Sep",
    October: "Oct",
    November: "Nov",
    December: "Dec",
  };

  let abbreviatedLabel = label;
  Object.entries(monthAbbreviations).forEach(([full, abbrev]) => {
    abbreviatedLabel = abbreviatedLabel.replace(full, abbrev);
  });

  return abbreviatedLabel;
};

const EventPopup: React.FC<{
  event: Event & { start: Date; end: Date; title: string };
  onClose: () => void;
  style: React.CSSProperties;
}> = ({ event, onClose, style }) => (
  <div
    className="event-popup absolute bg-white dark:bg-gray-800 rounded-md shadow-lg p-4 w-80 z-50 border border-gray-200 dark:border-gray-700"
    style={style}
    onMouseDown={(e) => e.stopPropagation()}
  >
    <button
      onMouseDown={onClose}
      className="absolute top-2 right-2 text-gray-800 dark:text-gray-300 w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700"
    >
      ✕
    </button>

    {event.source_image_url && (
      <div className="mb-3 -mx-4 -mt-4">
        <img
          src={event.source_image_url}
          alt={event.title}
          className="w-full h-40 object-cover rounded-t-lg"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = "none";
          }}
        />
      </div>
    )}

    <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-1 pr-8">
      {event.title}
    </h2>
    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
      {event.display_handle}
    </p>

    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
      <div className="flex items-center gap-2">
        <CalendarIcon className="h-4 w-4 flex-shrink-0" />
        <span>{formatEventDate(event.dtstart_utc, event.dtend_utc)}</span>
      </div>
      
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 flex-shrink-0" />
        <span>
          {formatTimeRange(event.dtstart_utc, event.dtend_utc)}
        </span>
      </div>
      
      {event.location && (
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 flex-shrink-0" />
          <span className="truncate" title={event.location}>
            {event.location}
          </span>
        </div>
      )}

      <div className="flex items-center gap-2">
        <DollarSign className="h-4 w-4 flex-shrink-0" />
        <span>
          {event.price === null || event.price === 0 ? "Free" : `$${event.price}`}
        </span>
      </div>

      {event.food && (
        <div className="flex items-center gap-2">
          <Utensils className="h-4 w-4 flex-shrink-0" />
          <span className="truncate" title={event.food}>
            {event.food}
          </span>
        </div>
      )}
      

      {event.registration && (
        <div className="italic">Registration required</div>
      )}

      {event.source_url && (
        <a
          href={event.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-blue-500 hover:underline"
          title={event.source_url}
        >
          <ExternalLink className="h-4 w-4 flex-shrink-0" />
          Event Link
        </a>
      )}
    </div>
  </div>
);

// Custom toolbar for < and > month buttons
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomToolbar: React.FC<ToolbarProps<any, object>> = ({
  label,
  onNavigate,
  onView,
  view,
}) => {
  return (
    <div className="relative mb-4 flex items-center justify-end gap-12">
      <div className="absolute left-0 sm:left-1/2 gap-3 sm:-translate-x-1/2 flex items-center ">
        {/* Back button < */}
        <IconButton
          onMouseDown={() => onNavigate("PREV")}
          icon={ChevronLeft}
          aria-label="Previous Month"
          size="sm"
        />

        {/* Month Year title */}
        <h2 className="text-lg whitespace-nowrap font-bold text-gray-900 dark:text-white">
          {abbreviateLabel(label)}
        </h2>

        {/* Next button > */}
        <IconButton
          onMouseDown={() => onNavigate("NEXT")}
          icon={ChevronRight}
          aria-label="Next Month"
          size="sm"
        />
      </div>

      {/* View tabs (Month/Week/Day) */}
      <Tabs value={view} onValueChange={(value) => onView(value as View)}>
        <TabsList>
          <TabsTrigger value="month">Month</TabsTrigger>
          <TabsTrigger value="week">Week</TabsTrigger>
          <TabsTrigger value="day">Day</TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  );
};

const EventsCalendar: React.FC<{ events: Event[] }> = ({ events }) => {
  const calendarContainerRef = useRef<HTMLDivElement>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Use react-use's useLocalStorage for view persistence, default to "day"
  const [currentView, setCurrentView] = useLocalStorage<View>("eventsCalendarView", "day");
  
  const [selectedEvent, setSelectedEvent] = useState<(Event & { start: Date; end: Date; title: string }) | null>(null);
  const [popupPosition, setPopupPosition] = useState<{ x: number; y: number } | null>(null);

  // Auto-scroll to 4pm (16:00) in day and week view
  useEffect(() => {
    if (currentView === "day" || currentView === "week") {
      // Use a small timeout to ensure the calendar has rendered
      const timer = setTimeout(() => {
        // Find the scrollable time content area
        const timeContent = document.querySelector('.rbc-time-content');
        if (timeContent) {
          // Each hour is typically 48px in react-big-calendar
          // Scroll to position that puts 4pm near the top of the viewport
          const scrollPosition = 8 * 48;
          timeContent.scrollTop = scrollPosition;
        }
      }, 150);

      return () => clearTimeout(timer);
    }
  }, [currentView, currentDate]); 

  const calendarEvents = events.map((event) => {
    const start = new Date(event.dtstart_utc);
    const end = event.dtend_utc
      ? new Date(event.dtend_utc)
      : new Date(start.getTime() + 60 * 60 * 1000); // Default end time = 1 hour after start
    return {
      ...event,
      title: event.title,
      start,
      end,
    };
  });

  // Custom styles for events based on club_type
  const eventPropGetter = (event: typeof calendarEvents[number]) => {
    const backgroundColor = getClubTypeColor(event.club_type);
    const baseStyle = {
      backgroundColor,
      borderRadius: "6px",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
      border: "1px solid rgba(0, 0, 0, 0.15)",
    };

    // Cap event width in day view to prevent them from taking up too much horizontal space
    if (currentView === "day") {
      return {
        style: {
          ...baseStyle,
          width: "25%",
          maxWidth: "200px",
          minWidth: "80px",
        },
      };
    }

    return {
      style: baseStyle,
    };
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

    // Calculate all possible positions relative to event
    const positions = {
      right: { x: rect.right + 10, y: rect.top },
      left: { x: rect.left - popupWidth - 10, y: rect.top },
      bottom: { x: rect.left, y: rect.bottom + 10 },
      top: { x: rect.left, y: rect.top - popupHeight - 10 },
    };

    // Score each position based on how well it fits
    let bestPosition = null;
    let bestScore = -1;

    for (const [name, pos] of Object.entries(positions)) {
      let score = 0;

      // Check if popup fits in viewport
      if (pos.x >= 0 && pos.x + popupWidth <= window.innerWidth) score += 10;
      if (pos.y >= 0 && pos.y + popupHeight <= window.innerHeight) score += 10;

      // Check if popup fits in container
      const containerX = pos.x - containerRect.left;
      const containerY = pos.y - containerRect.top;
      if (containerX >= 0 && containerX + popupWidth <= containerRect.width)
        score += 5;
      if (containerY >= 0 && containerY + popupHeight <= containerRect.height)
        score += 5;

      // Prefer right and bottom positions for better UX
      if (name === "right") score += 2;
      if (name === "bottom") score += 1;

      if (score > bestScore) {
        bestScore = score;
        bestPosition = pos;
      }
    }

    // Convert to container-relative coordinates or fallback to center
    let finalPosition;
    if (bestPosition && bestScore > 0) {
      finalPosition = {
        x: bestPosition.x - containerRect.left,
        y: bestPosition.y - containerRect.top,
      };
    } else {
      // Fallback to center if no good position found
      finalPosition = {
        x: Math.max(0, (containerRect.width - popupWidth) / 2),
        y: Math.max(0, (containerRect.height - popupHeight) / 2),
      };
    }

    setSelectedEvent(event);
    setPopupPosition(finalPosition);
  };

  const closePopup = () => {
    setSelectedEvent(null);
    setPopupPosition(null);
  };

  const handleNavigate = (newDate: Date) => {
    setCurrentDate(newDate);
  };

  return (
    <div 
      className="events-calendar-container relative" 
      onMouseDown={closePopup}
      ref={calendarContainerRef}
    >
      <Calendar
        localizer={localizer}
        events={calendarEvents}
        startAccessor="start"
        endAccessor="end"
        date={currentDate}
        onNavigate={handleNavigate}
        onView={setCurrentView}
        view={currentView}
        onSelectEvent={handleSelectEvent}
        components={{ toolbar: CustomToolbar }}
        formats={{
          // Shorten Day view header: e.g., Wed Oct 08
          dayHeaderFormat: (date, culture, loc) =>
            (loc || localizer).format(date, "EEE MMM dd", culture),
        }}
        eventPropGetter={eventPropGetter}
      />

      {selectedEvent && popupPosition && (
        <EventPopup
          event={selectedEvent}
          onClose={closePopup}
          style={{
            top: popupPosition.y,
            left: popupPosition.x,
          }}
        />
      )}
    </div>
  );
};

export default EventsCalendar;
