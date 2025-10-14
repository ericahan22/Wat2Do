export interface Club {
  id: number;
  club_name: string;
  categories: string[];
  club_page: string;
  ig: string;
  discord: string;
}

export interface SubmittedClub {
  id: string;
  club_name: string;
  categories: string;
  club_page?: string;
  ig?: string;
  discord?: string;
  club_type?: "WUSA" | "Athletics" | "Student Society";
  status: "scraped" | "pending" | "approved" | "rejected";
  submitted_at: string;
  rejection_reason?: string | null;
}

export interface ClubsResponse {
  clubs: Club[];
}
