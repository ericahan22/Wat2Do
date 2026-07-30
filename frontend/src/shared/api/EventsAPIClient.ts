import type { Event, EventDate } from "@/features/events/types/events";
import BaseAPIClient from "@/shared/api/BaseAPIClient";

export interface EventsQueryParams {
  search?: string;
  categories?: string;
  added_at?: string;
  start_utc?: string;
  end_utc?: string;
  cursor?: string;
  ids?: string;
  school?: string;
}

export interface EventsResponse {
  results: Event[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

interface ApiOccurrence {
  dtstart_utc: string;
  dtend_utc?: string | null;
}

interface ApiEvent {
  id: number;
  organization_id?: number | null;
  title: string;
  description?: string | null;
  location?: string | null;
  occurrences?: ApiOccurrence[];
  price?: number | null;
  food?: string[] | null;
  registration?: boolean;
  source_image_url?: string | null;
  organization_type?: string | null;
  school?: string | null;
  source_url?: string | null;
  category?: string | null;
  organization?: string | null;
  organization_page?: string | null;
  organization_ig?: string | null;
  organization_discord?: string | null;
  ig_handle?: string | null;
  cancelled?: boolean;
  added_at: string;
}

interface LatestAddedEvent {
  title: string;
  added_at: string;
}

interface ApiEventFeed {
  items: ApiEvent[];
  total: number;
  page: number;
  total_pages: number;
  latest_added_event?: LatestAddedEvent | null;
}

function appendList(searchParams: URLSearchParams, key: string, value?: string): void {
  value
    ?.split(/[;,]/)
    .map((item) => item.trim())
    .filter(Boolean)
    .forEach((item) => searchParams.append(key, item));
}

function buildFeedQuery(params: EventsQueryParams): string {
  const searchParams = new URLSearchParams({
    page: params.cursor || "1",
    page_size: "100",
  });

  if (params.school) searchParams.set("school_id", params.school);
  if (params.search) searchParams.set("search", params.search);
  if (params.start_utc) searchParams.set("start_utc", params.start_utc);
  if (params.end_utc) searchParams.set("end_utc", params.end_utc);
  if (params.added_at) searchParams.set("added_within_24h", "true");
  appendList(searchParams, "categories", params.categories);
  appendList(searchParams, "ids", params.ids);

  return searchParams.toString();
}

function sortedOccurrences(event: ApiEvent): EventDate[] {
  return (event.occurrences ?? [])
    .map((occurrence) => ({
      dtstart_utc: occurrence.dtstart_utc,
      dtend_utc: occurrence.dtend_utc ?? null,
    }))
    .sort(
      (first, second) =>
        new Date(first.dtstart_utc).getTime() -
        new Date(second.dtstart_utc).getTime(),
    );
}

function representativeOccurrence(event: ApiEvent): EventDate {
  const occurrences = sortedOccurrences(event);
  if (occurrences.length === 0) {
    return {
      dtstart_utc: event.added_at,
      dtend_utc: null,
    };
  }

  const now = Date.now();
  return (
    occurrences.find(
      (occurrence) => new Date(occurrence.dtstart_utc).getTime() >= now,
    ) ?? occurrences[occurrences.length - 1]
  );
}

function normalizeInstagramHandle(handle?: string | null): string | null {
  if (!handle) return null;
  try {
    const url = new URL(handle);
    if (!url.hostname.includes("instagram.com")) return null;
    const username = url.pathname.split("/").filter(Boolean)[0];
    return username ? `@${username}` : null;
  } catch {
    return handle.startsWith("@") ? handle : `@${handle}`;
  }
}

function normalizeEvent(event: ApiEvent): Event {
  const primaryDate = representativeOccurrence(event);
  const occurrences = sortedOccurrences(event);

  return {
    occurrence_key: `${event.id}:${primaryDate.dtstart_utc}`,
    id: event.id,
    organization_id: event.organization_id ?? null,
    title: event.title,
    description: event.description ?? "",
    location: event.location ?? "",
    dtstart_utc: primaryDate.dtstart_utc,
    dtend_utc: primaryDate.dtend_utc,
    price: event.price ?? null,
    food: event.food?.join(", ") ?? null,
    registration: event.registration ?? false,
    source_image_url: event.source_image_url ?? null,
    club_type: event.organization_type ?? null,
    category: event.category ?? null,
    added_at: event.added_at,
    school: event.school ?? null,
    status: event.cancelled ? "CANCELLED" : "CONFIRMED",
    ig_handle:
      normalizeInstagramHandle(event.organization_ig) ??
      normalizeInstagramHandle(event.ig_handle),
    discord_handle: event.organization_discord ?? null,
    x_handle: null,
    tiktok_handle: null,
    fb_handle: null,
    source_url: event.source_url ?? event.organization_page ?? null,
    display_handle: event.organization ?? event.ig_handle ?? "",
    occurrences: occurrences.length ? occurrences : [primaryDate],
  };
}

function escapeICS(value: string): string {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
}

function toICSDate(value: string): string {
  return new Date(value)
    .toISOString()
    .replace(/[-:]/g, "")
    .replace(/\.\d{3}Z$/, "Z");
}

function googleCalendarUrl(event: Event): string {
  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: event.title,
    dates: `${toICSDate(event.dtstart_utc)}/${toICSDate(
      event.dtend_utc ?? event.dtstart_utc,
    )}`,
    details: event.description || event.source_url || "",
    location: event.location || "",
  });
  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}

class EventsAPIClient {
  constructor(private apiClient: BaseAPIClient) { }

  async getEvents(params: EventsQueryParams = {}): Promise<EventsResponse> {
    const feed = await this.apiClient.get<ApiEventFeed>(
      `events/?${buildFeedQuery(params)}`,
    );
    if (!feed?.items) {
      return { results: [], nextCursor: null, hasMore: false, totalCount: 0 };
    }
    const events = feed.items.map(normalizeEvent);
    const hasMore = feed.page < feed.total_pages;

    return {
      results: events,
      nextCursor: hasMore ? String(feed.page + 1) : null,
      hasMore,
      totalCount: feed.total,
    };
  }

  async getLatestUpdate(
    school?: string,
  ): Promise<{ lastUpdated: string | null; latestEventTitle: string | null }> {
    const searchParams = new URLSearchParams({
      page: "1",
      page_size: "1",
      sort_by: "added_at",
      sort_order: "desc",
    });
    if (school) searchParams.set("school_id", school);
    const feed = await this.apiClient.get<ApiEventFeed>(
      `events/?${searchParams.toString()}`,
    );
    return {
      lastUpdated: feed?.latest_added_event?.added_at ?? null,
      latestEventTitle: feed?.latest_added_event?.title ?? null,
    };
  }

  async getEvent(eventId: number): Promise<Event> {
    return normalizeEvent(
      await this.apiClient.get<ApiEvent>(`events/${eventId}`),
    );
  }

  async exportEventsICS(events: Event[]): Promise<Blob> {
    const lines = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//wat2do//legacy-v1//EN",
      ...events.flatMap((event) => [
        "BEGIN:VEVENT",
        `UID:wat2do-${event.occurrence_key}@wat2do.ca`,
        `DTSTAMP:${toICSDate(new Date().toISOString())}`,
        `DTSTART:${toICSDate(event.dtstart_utc)}`,
        `DTEND:${toICSDate(event.dtend_utc ?? event.dtstart_utc)}`,
        `SUMMARY:${escapeICS(event.title)}`,
        `DESCRIPTION:${escapeICS(event.description || event.source_url || "")}`,
        `LOCATION:${escapeICS(event.location || "")}`,
        "END:VEVENT",
      ]),
      "END:VCALENDAR",
    ];

    return new Blob([lines.join("\r\n")], {
      type: "text/calendar;charset=utf-8",
    });
  }

  getGoogleCalendarUrls(events: Event[]): { urls: string[] } {
    return { urls: events.map(googleCalendarUrl) };
  }

  async getMyInterestedEventIds(): Promise<{ event_ids: number[] }> {
    const eventIds =
      await this.apiClient.get<number[]>("v1/saved-events/");
    return { event_ids: eventIds };
  }

  async markEventInterest(eventId: number): Promise<{ interested: boolean }> {
    await this.apiClient.put(`v1/saved-events/${eventId}`);
    return { interested: true };
  }

  async unmarkEventInterest(
    eventId: number,
  ): Promise<{ interested: boolean }> {
    await this.apiClient.delete(`v1/saved-events/${eventId}`);
    return { interested: false };
  }
}

export default EventsAPIClient;
