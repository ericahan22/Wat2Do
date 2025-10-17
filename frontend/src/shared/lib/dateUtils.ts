/**
 * Utility functions for formatting dates and times
 */


import { toZonedTime, format } from "date-fns-tz";


/**
 * Format a date string to a prettier format (e.g., "August 10, 2025")
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
    // Handle both ISO time format (HH:MM:SS) and time-only format
    let date: Date
    if (timeString.includes('T')) {
      // ISO datetime string
      date = new Date(timeString)
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

