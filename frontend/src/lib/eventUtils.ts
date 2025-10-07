import { Event } from "@/hooks";

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
