import { BaseAPIClient } from './BaseAPIClient';
import type { 
  PromoteEventRequest, 
  UpdatePromotionRequest, 
  PromoteEventResponse, 
  UpdatePromotionResponse, 
  UnpromoteEventResponse, 
  PromotedEventsResponse, 
  PromotionStatusResponse 
} from '@/features/admin/types/promotion';

export class AdminAPIClient extends BaseAPIClient {
  constructor() {
    super();
  }

  async promoteEvent(eventId: string, data: PromoteEventRequest = {}): Promise<PromoteEventResponse> {
    return this.post<PromoteEventResponse>(
      `/api/promotions/events/${eventId}/promote/`,
      data
    );
  }

  async updatePromotion(eventId: string, data: UpdatePromotionRequest): Promise<UpdatePromotionResponse> {
    return this.patch<UpdatePromotionResponse>(
      `/api/promotions/events/${eventId}/promote/`,
      data
    );
  }

  async unpromoteEvent(eventId: string): Promise<UnpromoteEventResponse> {
    return this.post<UnpromoteEventResponse>(
      `/api/promotions/events/${eventId}/unpromote/`
    );
  }

  async deletePromotion(eventId: string): Promise<void> {
    return this.delete<void>(
      `/api/promotions/events/${eventId}/promote/`
    );
  }

  async getPromotedEvents(): Promise<PromotedEventsResponse> {
    return this.get<PromotedEventsResponse>(
      '/api/promotions/events/promoted/'
    );
  }

  async getPromotionStatus(eventId: string): Promise<PromotionStatusResponse> {
    return this.get<PromotionStatusResponse>(
      `/api/promotions/events/${eventId}/promotion-status/`
    );
  }
}

// Export a default instance
export const adminAPIClient = new AdminAPIClient();
