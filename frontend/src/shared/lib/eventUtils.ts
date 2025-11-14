import { Event } from "@/features/events/types/events";

export const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  const startDateTime = new Date(event.dtstart_utc);
  const endDateTime = event.dtend_utc ? new Date(event.dtend_utc) : null;

  const nowTime = now.getTime();
  const startTime = startDateTime.getTime();
  const oneHourInMs = 60 * 60 * 1000;
  const twoHoursInMs = 2 * 60 * 60 * 1000;

  // For events with an end date, show "live" if current time is between start and end
  if (endDateTime) {
    const endTime = endDateTime.getTime();
    if (nowTime >= startTime && nowTime <= endTime) return "live";
  } else {
    // For events without an end date, show "live" if event has started and started within the last 2 hours
    const twoHoursAgo = nowTime - twoHoursInMs;
    if (startTime <= nowTime && startTime > twoHoursAgo) return "live";
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
  const startDateTime = new Date(event.dtstart_utc);
  const endDateTime = event.dtend_utc ? new Date(event.dtend_utc) : new Date(startDateTime.getTime() + 60 * 60 * 1000); // Default 1 hour if no end time
  
  return now < endDateTime;
};

/**
 * Maps submission status to badge variant
 * @param status - Submission status (approved, rejected, pending)
 * @returns Badge variant string
 */
export function getSubmissionStatusVariant(status: string): "success" | "destructive" | "warning" {
  if (status === "approved") return "success";
  if (status === "rejected") return "destructive";
  return "warning";
}
