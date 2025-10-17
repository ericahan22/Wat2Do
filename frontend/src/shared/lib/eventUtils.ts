import { Event } from "@/features/events/types/events";

export const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  const startDateTime = new Date(`${event.date}T${event.start_time}`);
  const endDateTime = new Date(`${event.date}T${event.end_time}`);

  const nowTime = now.getTime();
  const startTime = startDateTime.getTime();
  const endTime = endDateTime.getTime();
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
  const currentTime = new Date(`1970-01-01T${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:00`);
  
  const endTimeStr = event.end_time || 
    new Date(`1970-01-01T${event.start_time}`).getTime() + 60 * 60 * 1000; // +1 hour if no end_time
  const eventEndTime = new Date(`1970-01-01T${endTimeStr}`);
  
  return currentTime < eventEndTime;
};
