import { useState, useEffect } from "react";
import { Event } from "./useEvents";

import { API_BASE_URL } from '@/constants/api';

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

  const generateICS = (events: (Event & { description?: string | null; url?: string | null; })[]) => {
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
      if (event.description && event.description.trim().length > 0) {
        lines.push(`DESCRIPTION:${escapeText(event.description)}`);
      }
      if (event.location) {
        lines.push(`LOCATION:${escapeText(event.location)}`);
      }
      lines.push(`UID:${event.id}@wat2do.com`);
      lines.push('END:VEVENT');
    });

    lines.push('END:VCALENDAR');
    return lines.join('\r\n');
  };

  const exportToCalendar = async (events: Event[]) => {
    const eventsToExport = events.filter((event) => selectedEvents.has(event.id));
    const detailedEvents = await fetchEventDetails(eventsToExport.map(e => e.id));
    const enriched = mergeEventDetails(eventsToExport, detailedEvents);
    const icsContent = generateICS(enriched);
    
    // Check if user is on mobile device
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    if (isMobile) {
      // For mobile devices, use data URI to directly open calendar app
      // This works better on iOS Safari and Android
      const dataUri = `data:text/calendar;charset=utf-8,${encodeURIComponent(icsContent)}`;
      
      // Try to open in a new window first (works on some mobile browsers)
      const newWindow = window.open(dataUri, '_blank');
      
      // Fallback: if popup was blocked or didn't work, create a link
      if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
        const link = document.createElement('a');
        link.href = dataUri;
        link.download = 'events.ics';
        link.target = '_blank';
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Clean up after a delay
        setTimeout(() => {
          document.body.removeChild(link);
        }, 100);
      }
    } else {
      // Desktop: use blob URL approach
      const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'events.ics';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  const exportToGoogleCalendar = async (events: Event[]) => {
    const eventsToExport = events.filter((event) => selectedEvents.has(event.id));
    
    if (eventsToExport.length === 0) {
      return;
    }
    
    // Google Calendar only supports adding one event at a time via URL
    // So we'll open a new tab for the first event, or create multiple tabs if user wants
    // For better UX, let's create a single event if only one is selected, or batch them
    
    const detailedEvents = await fetchEventDetails(eventsToExport.map(e => e.id));
    const enriched = mergeEventDetails(eventsToExport, detailedEvents);

    enriched.forEach((event, index) => {
      // Parse the date and time
      const startDateTime = `${event.date}T${event.start_time}`;
      const endDateTime = event.end_time ? `${event.date}T${event.end_time}` : startDateTime;
      
      // Format dates for Google Calendar (need to remove hyphens and colons)
      const formatGoogleDate = (dateTime: string) => {
        return dateTime.replace(/[-:]/g, '');
      };
      
      const start = formatGoogleDate(startDateTime);
      const end = formatGoogleDate(endDateTime);
      
      // Build Google Calendar URL
      const params = new URLSearchParams({
        action: 'TEMPLATE',
        text: event.name,
        dates: `${start}/${end}`,
        details: event.description ? `${event.description}${event.url ? "\n\n" + event.url : ""}` : (event.url || ''),
        location: event.location || '',
      });
      
      const googleCalendarUrl = `https://calendar.google.com/calendar/render?${params.toString()}`;
      
      // Open in new tab with a small delay between each to avoid popup blocking
      setTimeout(() => {
        window.open(googleCalendarUrl, '_blank');
      }, index * 300);
    });
  };

  async function fetchEventDetails(ids: string[]) {
    if (ids.length === 0) return [] as Array<{ id: string; description?: string | null; url?: string | null; }>;
    const params = new URLSearchParams({ ids: ids.join(",") });
    const res = await fetch(`${API_BASE_URL}/api/events/details/?${params.toString()}`);
    if (!res.ok) return [];
    const data: { events: Array<{ id: string; description?: string | null; url?: string | null; }> } = await res.json();
    return data.events || [];
  }

  function mergeEventDetails(base: Event[], details: Array<{ id: string; description?: string | null; url?: string | null; }>) {
    const byId = new Map(details.map(d => [d.id, d] as const));
    return base.map(e => {
      const d = byId.get(e.id);
      return { ...e, description: d?.description ?? null, url: d?.url ?? e.url };
    });
  }

  return {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    clearSelection,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
  };
}
