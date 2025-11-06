import { Event } from "@/features/events/types/events";
import { removeTimezoneInfo } from "./dateUtils";

export const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  // Remove timezone info to treat as local time (not UTC)
  const startDateTime = new Date(removeTimezoneInfo(event.dtstart_utc));
  const endDateTime = event.dtend_utc ? new Date(removeTimezoneInfo(event.dtend_utc)) : null;

  const nowTime = now.getTime();
  const startTime = startDateTime.getTime();
  const oneHourInMs = 60 * 60 * 1000;
  const twoHoursInMs = 2 * 60 * 60 * 1000;

  // For events without an end date, show "live" if start date is after 2 hours before now
  if (!endDateTime) {
    const twoHoursAgo = nowTime - twoHoursInMs;
    if (startTime > twoHoursAgo) return "live";
  } else {
    // For events with an end date, show "live" if current time is between start and end
    const endTime = endDateTime.getTime();
    if (nowTime >= startTime && nowTime <= endTime) return "live";
  }

  // Show "soon" if event starts within the next hour
  if (startTime > nowTime && startTime - nowTime <= oneHourInMs) return "soon";

  return "none";
};

export const isEventNew = (event: Event): boolean => {
  if (!event.added_at) return false;

  const now = new Date();
  const addedAt = new Date(event.added_at);
  
  // New events are those added in past 24 hours
  return (now.getTime() - addedAt.getTime()) <= 24 * 60 * 60 * 1000;
};

/**
 * Check if an event is still ongoing (current time < end time)
 */
export const isEventOngoing = (event: Event): boolean => {
  const now = new Date();
  // Remove timezone info to treat as local time (not UTC)
  const startDateTime = new Date(removeTimezoneInfo(event.dtstart_utc));
  const endDateTime = event.dtend_utc ? new Date(removeTimezoneInfo(event.dtend_utc)) : new Date(startDateTime.getTime() + 60 * 60 * 1000); // Default 1 hour if no end time
  
  return now < endDateTime;
};
