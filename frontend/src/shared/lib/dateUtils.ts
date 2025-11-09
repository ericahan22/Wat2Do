import { format } from "date-fns-tz";

const toMidnight = (date: Date) =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate());
const sameDay = (firstDate: Date, secondDate: Date) =>
  firstDate.toDateString() === secondDate.toDateString();

/** "Wed Jan 15 to Thu Jan 16" | "Wednesday Jan 15" */
export const formatEventDate = (
  startUtcString: string,
  endUtcString?: string | null
): string => {
  const startDate = new Date(startUtcString);
  if (!endUtcString) return format(startDate, "EEEE MMM d");
  const endDate = new Date(endUtcString);
  return sameDay(toMidnight(startDate), toMidnight(endDate))
    ? format(startDate, "EEEE MMM d")
    : `${format(startDate, "EEE MMM d")} to ${format(endDate, "EEE MMM d")}`;
};

/** "3:30 PM" (hides :00) */
export const formatPrettyTime = (utcString: string): string =>
  new Date(utcString).toLocaleTimeString().replace(":00", "");

/** "YYYY-MM-DD" */
export const getTodayString = (): string =>
  new Date().toISOString().slice(0, 10);

/** "3 PM - 5 PM" | "3 PM" */
export const formatTimeRange = (
  startUtcString: string,
  endUtcString: string | null
): string => {
  const startTime = formatPrettyTime(startUtcString),
    endTime = endUtcString ? formatPrettyTime(endUtcString) : null;
  return endTime ? `${startTime} - ${endTime}` : startTime;
};

/** "today" | "tomorrow" | "later this week" | "later this month" | "later" | "past" */
export const getDateCategory = (
  startUtcString: string,
  endUtcString?: string | null
):
  | "today"
  | "tomorrow"
  | "later this week"
  | "later this month"
  | "later"
  | "past" => {
  const startDate = toMidnight(new Date(startUtcString)),
    endDate = toMidnight(endUtcString ? new Date(endUtcString) : startDate),
    todayDate = toMidnight(new Date()),
    tomorrowDate = toMidnight(new Date(Date.now() + 86400000)),
    endOfWeek = toMidnight(
      new Date(
        todayDate.getFullYear(),
        todayDate.getMonth(),
        todayDate.getDate() + ((7 - todayDate.getDay()) % 7)
      )
    ),
    endOfMonth = toMidnight(
      new Date(todayDate.getFullYear(), todayDate.getMonth() + 1, 0)
    );

  if (todayDate >= startDate && todayDate <= endDate) return "today";
  if (
    (tomorrowDate >= startDate && tomorrowDate <= endDate) ||
    sameDay(startDate, tomorrowDate)
  )
    return "tomorrow";
  if (endDate < todayDate) return "past";
  if (startDate <= endOfWeek) return "later this week";
  if (startDate <= endOfMonth) return "later this month";
  return "later";
};

/** "Today 6:43 PM EST" | "Yesterday 6:43 PM EST" | "Monday 6:43 PM EST" */
export const formatRelativeDateTime = (utcString: string): string => {
  const targetDate = new Date(utcString),
    currentDate = new Date(),
    previousDate = new Date(currentDate);
  previousDate.setDate(currentDate.getDate() - 1);
  const targetDay = toMidnight(targetDate),
    todayDay = toMidnight(currentDate),
    yesterdayDay = toMidnight(previousDate),
    formattedTime = format(targetDate, "h:mm a zzz");
  if (targetDay.getTime() === todayDay.getTime())
    return `Today ${formattedTime}`;
  if (targetDay.getTime() === yesterdayDay.getTime())
    return `Yesterday ${formattedTime}`;
  return format(targetDate, "EEEE h:mm a zzz");
};

/** "Today" else formatted date */
export const formatRelativeEventDate = (
  startUtcString: string,
  endUtcString?: string | null
): string => {
  const startDate = toMidnight(new Date(startUtcString)),
    endDate = toMidnight(endUtcString ? new Date(endUtcString) : startDate),
    todayDate = toMidnight(new Date());
  return todayDate >= startDate && todayDate <= endDate
    ? "Today"
    : formatEventDate(startUtcString, endUtcString);
};

/** "Today, 1 PM - 4 PM" | "Monday Jan 20, 1 PM" */
export const formatRelativeEventDateWithTime = (
  startUtcString: string,
  endUtcString?: string | null
): string =>
  `${formatRelativeEventDate(
    startUtcString,
    endUtcString || null
  )}, ${formatTimeRange(startUtcString, endUtcString || null)}`;

/** Convert UTC ISO string to local datetime-local format (YYYY-MM-DDTHH:mm) */
export const utcToLocal = (utcString: string): string => {
  if (!utcString) return "";
  return new Date(utcString)
    .toLocaleString("sv-SE")
    .replace(" ", "T")
    .slice(0, 16);
};

/** Convert local datetime-local string to UTC ISO string */
export const localToUtc = (localString: string): string => {
  if (!localString) return "";
  return new Date(localString).toISOString();
};
