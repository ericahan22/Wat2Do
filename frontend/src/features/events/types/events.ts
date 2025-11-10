export interface EventDate {
  dtstart_utc: string;
  dtend_utc: string | null;
}

export interface Event {
  id: number;
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
  added_at: string;
  school: string | null;
  status: string; // Event status: PENDING, CONFIRMED, etc.
  ig_handle: string | null;
  discord_handle: string | null;
  x_handle: string | null;
  tiktok_handle: string | null;
  fb_handle: string | null;
  source_url: string | null;
  display_handle: string; // Computed field from backend
  interest_count: number; // Number of users interested in this event
  occurrences?: EventDate[]; // Multiple occurrence dates for recurring events
  is_submitter?: boolean; // Whether the current user is the submitter of this event
}

export interface EventsResponse {
  results: Event[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

export type EventView = "grid" | "calendar";
