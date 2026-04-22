export interface AutomateLog {
  id: number;
  ig_user_id: string | null;
  ig_username: string | null;
  username_resolved: boolean;
  dispatch_sent: boolean;
  error_message: string | null;
  created_at: string;
}

export interface AutomateLogsResponse {
  logs: AutomateLog[];
  total: number;
  unresolved_count: number;
}

export interface ScrapeRun {
  id: number;
  ig_username: string;
  github_run_id: string | null;
  status: "running" | "success" | "error" | "no_posts";
  posts_fetched: number;
  posts_new: number;
  events_extracted: number;
  events_saved: number;
  pinned_post_warning: boolean;
  error_message: string | null;
  started_at: string;
  finished_at: string | null;
}

export interface ScrapeRunsResponse {
  runs: ScrapeRun[];
  total: number;
}

export interface GapAccount {
  ig_handle: string;
  club_name: string;
  last_notification_at: string | null;
  last_scrape_at: string | null;
  last_scrape_status: string | null;
  last_event_at: string | null;
  last_event_title: string | null;
  gap_days: number | null;
  status: "active" | "stale" | "never_scraped" | "error";
}

export interface GapAnalysisResponse {
  accounts: GapAccount[];
  summary: {
    total_clubs: number;
    active_recently: number;
    stale: number;
    never_scraped: number;
  };
}
