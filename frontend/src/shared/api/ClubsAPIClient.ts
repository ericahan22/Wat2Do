import type { Club } from '@/features/clubs/types/clubs';
import BaseAPIClient from '@/shared/api/BaseAPIClient';

export interface ClubsResponse {
  results: Club[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

export interface ClubsQueryParams {
  search?: string;
  category?: string;
  limit?: number;
  cursor?: string;
}

// Helper function to build query string (DRY principle)
function buildQueryString(params: ClubsQueryParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, item.toString()));
      } else {
        searchParams.append(key, value.toString());
      }
    }
  });
  return searchParams.toString();
}

/**
 * Clubs API Client - Clean class pattern!
 * Takes BaseAPIClient as constructor parameter
 */
class ClubsAPIClient {
  /**
   * @param {BaseAPIClient} apiClient A pre-configured instance of the base API client.
   */
  constructor(private apiClient: BaseAPIClient) {}

  /**
   * Fetches clubs from the backend with cursor-based pagination.
   * Corresponds to a GET request to /api/clubs/
   */
  async getClubs(params: ClubsQueryParams = {}): Promise<ClubsResponse> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `clubs/?${queryString}` : 'clubs/';
    return this.apiClient.get(endpoint);
  }

  /**
   * Fetches a single club by its ID.
   * Corresponds to a GET request to /api/clubs/{id}/
   */
  async getClubById(clubId: string): Promise<Club> {
    return this.apiClient.get(`clubs/${clubId}/`);
  }


  /**
   * Searches clubs by name or description.
   * Corresponds to a GET request to /api/clubs/search/
   */
  async searchClubs(query: string, limit?: number): Promise<Club[]> {
    const params = new URLSearchParams({ q: query });
    if (limit) params.append('limit', limit.toString());
    return this.apiClient.get(`clubs/search/?${params.toString()}`);
  }

  /**
   * Gets clubs by category.
   * Corresponds to a GET request to /api/clubs/category/{category}/
   */
  async getClubsByCategory(category: string): Promise<Club[]> {
    return this.apiClient.get(`clubs/category/${encodeURIComponent(category)}/`);
  }
}

export default ClubsAPIClient;