export interface EventDate {
  dtstart_utc: string;
  dtend_utc: string | null;
}

export interface Event {
  id: number;
  title: string;
  description: string;
  location: string;
  dtstart?: string; // Local datetime string
  dtend?: string | null; // Local datetime string
  dtstart_utc: string; // ISO datetime string
  dtend_utc: string | null; // ISO datetime string
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
  upcoming_dates?: EventDate[]; // Multiple occurrence dates for recurring events
}

export interface EventsResponse {
  results: Event[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

export type EventView = "grid" | "calendar";
