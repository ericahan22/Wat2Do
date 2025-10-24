/**
 * Utility functions for formatting dates and times
 */


import { format } from "date-fns-tz";

/**
 * Remove timezone info from ISO datetime string to treat as local time
 */
export const removeTimezoneInfo = (dateTimeString: string): string => {
  return dateTimeString.replace(/[+-]\d{2}:\d{2}$/, '');
};


/**
 * Format a date string to a prettier format (e.g., "Friday, Sep 30")
 * Can handle both date strings (YYYY-MM-DD) and ISO datetime strings
 */
export const formatPrettyDate = (dateString: string): string => {
  try {
    const date = new Date(removeTimezoneInfo(dateString));
    return format(date, "EEEE, MMM d");
  } catch {
    return dateString // Return original string if parsing fails
  }
}

/**
 * Format a time string to a prettier format (e.g., "3pm" or "3:30pm")
 */
export const formatPrettyTime = (timeString: string): string => {
  try {
    let date: Date
    if (timeString.includes('T')) {
      // For UTC timestamps that are already in local time, remove timezone info
      // and create date as if it's local time
      const localTimeString = removeTimezoneInfo(timeString);
      date = new Date(localTimeString);
    } else {
      // Time-only string (HH:MM:SS or HH:MM)
      date = new Date(`1970-01-01T${timeString}`)
    }
    
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: date.getMinutes() === 0 ? undefined : '2-digit',
      hour12: true
    }).toLowerCase()
  } catch {
    return timeString // Return original string if parsing fails
  }
}

/**
 * Format a time range (e.g., "3pm - 8pm")
 */
export const formatTimeRange = (startTime: string, endTime: string | null): string => {
  const start = formatPrettyTime(startTime)
  const end = endTime ? formatPrettyTime(endTime) : null
  return end ? `${start} - ${end}` : start
}

/**
 * Get today's date as a string in YYYY-MM-DD format
 */
export const getTodayString = (): string => {
  const now = new Date();
  return (
    now.getFullYear() +
    "-" +
    String(now.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(now.getDate()).padStart(2, "0")
  );
};

/**
 * Format a time range from ISO datetime strings (e.g., "3pm - 8pm")
 */
export const formatEventTimeRange = (startDateTime: string, endDateTime: string | null): string => {
  const start = formatPrettyTime(startDateTime);
  const end = endDateTime ? formatPrettyTime(endDateTime) : null;
  return end ? `${start} - ${end}` : start;
};

/**
 * Format dtstart to YYYY-MM-DDT00:00:00 format
 */
export const formatDtstartToMidnight = (dtstart: string): string => {
  const date = dtstart.split('T')[0];
  return `${date}T00:00:00`;
};

/**
 * Get date category for event grouping (today, tomorrow, later this week, later this month, later, past)
 */
export const getDateCategory = (dateString: string): 'today' | 'tomorrow' | 'later this week' | 'later this month' | 'later' | 'past' => {
  try {
    const eventDate = new Date(removeTimezoneInfo(dateString));
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    // Get end of this week (Sunday)
    const endOfWeek = new Date(today);
    const daysUntilSunday = (7 - today.getDay()) % 7;
    endOfWeek.setDate(today.getDate() + daysUntilSunday);
    
    // Get end of this month
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    // Reset time to start of day for comparison
    const eventDateOnly = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const tomorrowOnly = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate());
    const endOfWeekOnly = new Date(endOfWeek.getFullYear(), endOfWeek.getMonth(), endOfWeek.getDate());
    const endOfMonthOnly = new Date(endOfMonth.getFullYear(), endOfMonth.getMonth(), endOfMonth.getDate());
    
    if (eventDateOnly.getTime() === todayOnly.getTime()) {
      return 'today';
    } else if (eventDateOnly.getTime() === tomorrowOnly.getTime()) {
      return 'tomorrow';
    } else if (eventDateOnly.getTime() < todayOnly.getTime()) {
      return 'past';
    } else if (eventDateOnly.getTime() <= endOfWeekOnly.getTime()) {
      return 'later this week';
    } else if (eventDateOnly.getTime() <= endOfMonthOnly.getTime()) {
      return 'later this month';
    } else {
      return 'later';
    }
  } catch {
    return 'later';
  }
};

/**
 * Format a date string with relative date and time (e.g., "Yesterday 6:43PM EST", "Today 6:43PM EST", "Thursday 7:34PM EST")
 */
export const formatRelativeDateTime = (dateString: string): string => {
  try {
    // Parse the date string directly - JavaScript will handle UTC conversion automatically
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    
    // Reset time to start of day for comparison
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const yesterdayOnly = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate());
    
    const timeStr = format(date, "h:mm a zzz");
    
    if (dateOnly.getTime() === todayOnly.getTime()) {
      return `Today ${timeStr}`;
    } else if (dateOnly.getTime() === yesterdayOnly.getTime()) {
      return `Yesterday ${timeStr}`;
    } else {
      return format(date, "EEEE h:mm a zzz");
    }
  } catch {
    return dateString;
  }
};

