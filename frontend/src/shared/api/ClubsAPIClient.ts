import type { Club } from '@/features/clubs/types/clubs';

export interface ClubsResponse {
  clubs: Club[];
  count: number;
}

export interface ClubsQueryParams {
  search?: string;
  categories?: string[];
  limit?: number;
  offset?: number;
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
  constructor(private apiClient: any) {}

  /**
   * Fetches all clubs from the backend.
   * Corresponds to a GET request to /api/clubs/
   */
  async getClubs(params: ClubsQueryParams = {}): Promise<Club[]> {
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
   * Gets clubs response with count.
   * Corresponds to a GET request to /api/clubs/ with count
   */
  async getClubsWithCount(params: ClubsQueryParams = {}): Promise<ClubsResponse> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `clubs/?${queryString}&count=true` : 'clubs/?count=true';
    return this.apiClient.get(endpoint);
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