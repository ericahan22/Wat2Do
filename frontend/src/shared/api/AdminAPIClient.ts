import type { 
  PromoteEventRequest, 
  UpdatePromotionRequest, 
  PromoteEventResponse, 
  UpdatePromotionResponse, 
  UnpromoteEventResponse, 
  PromotedEventsResponse, 
  PromotionStatusResponse 
} from '@/features/admin/types/promotion';
import BaseAPIClient from './BaseAPIClient';

/**
 * Admin API Client - Clean class pattern!
 * Takes BaseAPIClient as constructor parameter
 */
class AdminAPIClient {
  /**
   * @param {BaseAPIClient} apiClient A pre-configured instance of the base API client.
   */
  constructor(private apiClient: BaseAPIClient) {}

  /**
   * Promotes an event.
   * Corresponds to a POST request to /api/promotions/events/{eventId}/promote/
   */
  async promoteEvent(eventId: string, data: PromoteEventRequest = {}): Promise<PromoteEventResponse> {
    return this.apiClient.post(`promotions/events/${eventId}/promote/`, data);
  }

  /**
   * Updates a promotion.
   * Corresponds to a PUT request to /api/promotions/{promotionId}/
   */
  async updatePromotion(promotionId: string, data: UpdatePromotionRequest): Promise<UpdatePromotionResponse> {
    return this.apiClient.put(`promotions/${promotionId}/`, data);
  }

  /**
   * Unpromotes an event.
   * Corresponds to a DELETE request to /api/promotions/events/{eventId}/unpromote/
   */
  async unpromoteEvent(eventId: string): Promise<UnpromoteEventResponse> {
    return this.apiClient.delete(`promotions/events/${eventId}/unpromote/`);
  }

  /**
   * Gets all promoted events.
   * Corresponds to a GET request to /api/promotions/events/
   */
  async getPromotedEvents(): Promise<PromotedEventsResponse> {
    return this.apiClient.get('promotions/events/');
  }

  /**
   * Gets promotion status for an event.
   * Corresponds to a GET request to /api/promotions/events/{eventId}/status/
   */
  async getPromotionStatus(eventId: string): Promise<PromotionStatusResponse> {
    return this.apiClient.get(`promotions/events/${eventId}/status/`);
  }

  /**
   * Deletes a promotion.
   * Corresponds to a DELETE request to /api/promotions/{promotionId}/
   */
  async deletePromotion(promotionId: string): Promise<{ message: string }> {
    return this.apiClient.delete(`promotions/${promotionId}/`);
  }
}

export default AdminAPIClient;