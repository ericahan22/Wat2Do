export interface Event {
  id: number;
  title: string;
  description: string;
  location: string;
  longitude: number | null;
  latitude: number | null;
  dtstart_utc: string; // ISO datetime string
  dtend_utc: string | null; // ISO datetime string
  price: number | null;
  food: string | null;
  registration: boolean;
  source_image_url: string | null;
  club_type: string | null;
  added_at: string;
  school: string | null;
  ig_handle: string | null;
  discord_handle: string | null;
  x_handle: string | null;
  tiktok_handle: string | null;
  fb_handle: string | null;
  source_url: string | null;
  display_handle: string; // Computed field from backend
}

export interface EventsResponse {
  event_ids: string[];
}

export type EventView = "grid" | "calendar";
