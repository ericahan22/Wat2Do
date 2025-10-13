export interface Club {
  id: number;
  club_name: string;
  categories: string[];
  club_page: string;
  ig: string;
  discord: string;
}

export interface ClubsResponse {
  clubs: Club[];
}
