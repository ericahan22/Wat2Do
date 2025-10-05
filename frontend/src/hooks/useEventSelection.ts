import { useState, useEffect } from "react";
import { Event } from "./useEvents";

export function useEventSelection(view: "grid" | "calendar") {
  const [isSelectMode, setIsSelectMode] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState<Set<string>>(new Set());

  // Auto-clear selection when switching to calendar view
  useEffect(() => {
    if (view === "calendar") {
      setIsSelectMode(false);
      setSelectedEvents(new Set());
    }
  }, [view]);

  const toggleSelectMode = () => {
    setIsSelectMode(!isSelectMode);
    if (isSelectMode) {
      setSelectedEvents(new Set());
    }
  };

  const clearSelection = () => {
    setIsSelectMode(false);
    setSelectedEvents(new Set());
  };

  const toggleEventSelection = (eventId: string) => {
    setSelectedEvents((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const generateICS = (events: Event[]) => {
    const lines = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//Wat2Do//Events//EN',
      'CALSCALE:GREGORIAN',
    ];

    // Helper to escape special characters in iCalendar format
    const escapeText = (text: string) => {
      return text.replace(/\\/g, '\\\\')
                 .replace(/;/g, '\\;')
                 .replace(/,/g, '\\,')
                 .replace(/\n/g, '\\n');
    };

    // Current timestamp in UTC for DTSTAMP
    const now = new Date();
    const dtstamp = now.toISOString().replace(/[-:]/g, '').split('.')[0];

    events.forEach((event) => {
      const startDate = event.date.replace(/-/g, '');
      const startTime = event.start_time.replace(/:/g, '');
      const endTime = event.end_time ? event.end_time.replace(/:/g, '') : startTime;

      lines.push('BEGIN:VEVENT');
      lines.push(`DTSTART:${startDate}T${startTime}`);
      lines.push(`DTEND:${startDate}T${endTime}`);
      lines.push(`DTSTAMP:${dtstamp}`);
      lines.push(`SUMMARY:${escapeText(event.name)}`);
      if (event.location) {
        lines.push(`LOCATION:${escapeText(event.location)}`);
      }
      lines.push(`UID:${event.id}@wat2do.com`);
      lines.push('END:VEVENT');
    });

    lines.push('END:VCALENDAR');
    return lines.join('\r\n');
  };

  const exportToCalendar = (events: Event[]) => {
    const eventsToExport = events.filter((event) => selectedEvents.has(event.id));
    const icsContent = generateICS(eventsToExport);
    
    const blob = new Blob([icsContent], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'events.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    clearSelection,
    toggleEventSelection,
    exportToCalendar,
  };
}
