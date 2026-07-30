export interface EventDate {
  dtstart_utc: string;
  dtend_utc: string | null;
}

export interface Event {
  occurrence_key: string;
  id: number;
  organization_id: number | null;
  title: string;
  description: string;
  location: string;
  dtstart_utc: string; // ISO datetime string (UTC)
  dtend_utc: string | null; // ISO datetime string (UTC)
  price: number | null;
  food: string | null;
  registration: boolean;
  source_image_url: string | null;
  club_type: string | null;
  category?: string | null;
  added_at: string;
  school: string | null;
  status: string; // Event status: PENDING, CONFIRMED, etc.
  ig_handle: string | null;
  discord_handle: string | null;
  x_handle: string | null;
  tiktok_handle: string | null;
  fb_handle: string | null;
  source_url: string | null;
  display_handle: string; // Computed from the V2 response
  occurrences?: EventDate[]; // Multiple occurrence dates for recurring events
}

export interface EventsResponse {
  results: Event[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

export type EventView = "grid" | "calendar";
