import { Event } from "@/features/events/types/events";

export const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  const startDateTime = new Date(event.dtstart);
  const endDateTime = event.dtend ? new Date(event.dtend) : null;

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
  const nineteenHoursInMs = 19 * 60 * 60 * 1000;

  return now.getTime() - addedAt.getTime() <= nineteenHoursInMs;
};

/**
 * Check if an event is still ongoing (current time < end time)
 */
export const isEventOngoing = (event: Event): boolean => {
  const now = new Date();
  const startDateTime = new Date(event.dtstart);
  const endDateTime = event.dtend ? new Date(event.dtend) : new Date(startDateTime.getTime() + 60 * 60 * 1000); // Default 1 hour if no end time
  
  return now < endDateTime;
};
