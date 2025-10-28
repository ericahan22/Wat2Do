import { BaseAPIClient } from './BaseAPIClient';
import type { Club } from '@/features/clubs/types/clubs';

export interface ClubsResponse {
  clubs: Club[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface ClubsQueryParams {
  search?: string;
  limit?: number;
  offset?: number;
}

export class ClubsAPIClient extends BaseAPIClient {
  constructor() {
    super();
  }

  async getClubs(params: ClubsQueryParams = {}): Promise<Club[]> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/api/clubs/?${queryString}` : '/api/clubs/';
    
    return this.get<Club[]>(endpoint);
  }

  async getClub(clubId: number): Promise<Club> {
    return this.get<Club>(`/api/clubs/${clubId}/`);
  }
}

// Export a default instance
export const clubsAPIClient = new ClubsAPIClient();
