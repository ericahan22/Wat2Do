/**
 * Type definitions for event promotion feature
 * Using separate EventPromotion table (Option 2)
 */

/**
 * Promotion types
 */
export type PromotionType = 'standard' | 'featured' | 'urgent' | 'sponsored';

/**
 * Promotion data returned from API
 */
export interface EventPromotion {
  is_active: boolean;
  promoted_at: string; // ISO 8601 datetime
  promoted_by: string;
  expires_at: string | null; // ISO 8601 datetime
  priority: number; // 0-10
  promotion_type: PromotionType;
  notes?: string;
}

/**
 * Event with embedded promotion data
 */
export interface PromotedEvent {
  id: number;
  title: string;
  dtstart_utc: string;
  dtend_utc: string | null;
  location: string;
  description: string | null;
  source_image_url: string | null;
  display_handle: string;
  promotion: EventPromotion;
}

/**
 * Request payload for promoting an event
 */
export interface PromoteEventRequest {
  priority?: number; // 0-10, default 0
  expires_at?: string; // ISO 8601 datetime
  promoted_by?: string; // Optional, defaults to current user
  promotion_type?: PromotionType; // Default 'standard'
  notes?: string; // Internal notes
}

/**
 * Request payload for updating a promotion
 */
export interface UpdatePromotionRequest {
  priority?: number;
  expires_at?: string | null;
  promotion_type?: PromotionType;
  notes?: string;
}

/**
 * Response from promote endpoint
 */
export interface PromoteEventResponse {
  message: string;
  event_id: string;
  promotion: EventPromotion;
}

/**
 * Response from update promotion endpoint
 */
export interface UpdatePromotionResponse {
  message: string;
  event_id: string;
  promotion: Partial<EventPromotion>;
}

/**
 * Response from unpromote endpoint
 */
export interface UnpromoteEventResponse {
  message: string;
  event_id: string;
}

/**
 * Response from get promoted events endpoint
 */
export interface PromotedEventsResponse {
  promoted_events: PromotedEvent[];
}

/**
 * Response from get promotion status endpoint
 */
export interface PromotionStatusResponse {
  event_id: string;
  event_name: string;
  is_promoted: boolean;
  promotion: EventPromotion | null;
}

/**
 * Form state for promotion form
 */
export interface PromotionFormData {
  priority: number;
  expiresAt: string; // For datetime-local input
  promotedBy: string;
  promotionType: PromotionType;
  notes: string;
}

/**
 * Error response from promotion endpoints
 */
export interface PromotionErrorResponse {
  error: string;
  details?: Record<string, unknown>;
}

