/**
 * Utility functions for formatting dates and times
 */


import { toZonedTime, format } from "date-fns-tz";

/**
 * Remove timezone info from ISO datetime string to treat as local time
 */
export const removeTimezoneInfo = (dateTimeString: string): string => {
  return dateTimeString.replace(/[+-]\d{2}:\d{2}$/, '');
};


/**
 * Format a date string to a prettier format (e.g., "August 10, 2025")
 * Can handle both date strings (YYYY-MM-DD) and ISO datetime strings
 */
export const formatPrettyDate = (dateString: string): string => {
  try {
    const tz = "America/New_York";
    const date = toZonedTime(dateString, tz);
    return format(date, "MMMM d, yyyy");
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
 * Format an ISO datetime string to a prettier date format (e.g., "August 10, 2025")
 */
export const formatEventDate = (isoDateTime: string): string => {
  return formatPrettyDate(isoDateTime);
};

/**
 * Format an ISO datetime string to a prettier time format (e.g., "3pm" or "3:30pm")
 */
export const formatEventTime = (isoDateTime: string): string => {
  return formatPrettyTime(isoDateTime);
};

/**
 * Format a time range from ISO datetime strings (e.g., "3pm - 8pm")
 */
export const formatEventTimeRange = (startDateTime: string, endDateTime: string | null): string => {
  const start = formatEventTime(startDateTime);
  const end = endDateTime ? formatEventTime(endDateTime) : null;
  return end ? `${start} - ${end}` : start;
};

/**
 * Format dtstart to YYYY-MM-DDT00:00:00 format
 */
export const formatDtstartToMidnight = (dtstart: string): string => {
  const date = dtstart.split('T')[0];
  return `${date}T00:00:00`;
};

