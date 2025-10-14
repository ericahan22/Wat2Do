export interface Event {
  id: string;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string | null;
  location: string;
  image_url: string | null;
  categories?: string[];
  price: number | null;
  food: string | null;
  registration: boolean;
  club_type?: "WUSA" | "Athletics" | "Student Society" | null;
  added_at: string;
}

export interface SubmittedEvent {
  id: string;
  club_handle: string;
  url: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string | null;
  location: string;
  price: number | null;
  food: string | null;
  registration: boolean;
  image_url: string | null;
  description: string | null;
  club_type?: "WUSA" | "Athletics" | "Student Society" | null;
  status: "scraped" | "pending" | "approved" | "rejected";
  submitted_at: string;
  rejection_reason?: string | null;
}

export interface EventsResponse {
  event_ids: string[];
}

export type EventView = "grid" | "calendar";
