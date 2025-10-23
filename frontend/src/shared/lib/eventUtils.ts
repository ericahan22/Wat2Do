import { Event } from "@/features/events/types/events";
import { removeTimezoneInfo } from "./dateUtils";

export const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  // Remove timezone info to treat as local time (not UTC)
  const startDateTime = new Date(removeTimezoneInfo(event.dtstart));
  const endDateTime = event.dtend ? new Date(removeTimezoneInfo(event.dtend)) : null;

  const nowTime = now.getTime();
  const startTime = startDateTime.getTime();
  const endTime = endDateTime ? endDateTime.getTime() : startTime + (60 * 60 * 1000); // Default 1 hour if no end time
  const oneHourInMs = 60 * 60 * 1000;

  if (nowTime >= startTime && nowTime <= endTime) return "live";

  if (startTime > nowTime && startTime - nowTime <= oneHourInMs) return "soon";

  return "none";
};

export const isEventNew = (event: Event): boolean => {
  if (!event.added_at) return false;

  const now = new Date();
  const addedAt = new Date(event.added_at);
  
  // Match the logic from handleToggleNewEvents
  const todayAt7am = new Date();
  todayAt7am.setHours(7, 0, 0, 0);
  
  const cutoffDate = now >= todayAt7am ? todayAt7am : new Date(todayAt7am.getTime() - 24 * 60 * 60 * 1000);
  
  return addedAt >= cutoffDate;
};

/**
 * Check if an event is still ongoing (current time < end time)
 */
export const isEventOngoing = (event: Event): boolean => {
  const now = new Date();
  // Remove timezone info to treat as local time (not UTC)
  const startDateTime = new Date(removeTimezoneInfo(event.dtstart));
  const endDateTime = event.dtend ? new Date(removeTimezoneInfo(event.dtend)) : new Date(startDateTime.getTime() + 60 * 60 * 1000); // Default 1 hour if no end time
  
  return now < endDateTime;
};
