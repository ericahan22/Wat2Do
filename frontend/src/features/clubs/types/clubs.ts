export interface Club {
  id: number;
  club_name: string;
  categories: string[];
  club_page: string;
  ig: string;
  discord: string;
  club_type: string;
  logo_url: string | null;
  school: string | null;
}

export interface ClubsResponse {
  clubs: Club[];
}
