// Base API Client
export { BaseAPIClient, baseAPIClient, ApiError } from './BaseAPIClient';
export type { ApiResponse, RequestConfig } from './BaseAPIClient';

// Feature-specific API Clients
export { AuthAPIClient, authAPIClient } from './AuthAPIClient';
export type { User, LoginRequest, SignupRequest, AuthResponse } from '@/features/auth/types/auth';

export { EventsAPIClient, eventsAPIClient } from './EventsAPIClient';
export type { Event, EventsQueryParams, EventSubmissionResponse } from './EventsAPIClient';

export { AdminAPIClient, adminAPIClient } from './AdminAPIClient';
export type { 
  PromoteEventRequest, 
  UpdatePromotionRequest, 
  PromoteEventResponse,
  UpdatePromotionResponse,
  UnpromoteEventResponse,
  PromotedEventsResponse,
  PromotionStatusResponse
} from '@/features/admin/types/promotion';

export { NewsletterAPIClient, newsletterAPIClient } from './NewsletterAPIClient';
export type { 
  NewsletterSubscribeRequest, 
  NewsletterSubscribeResponse,
  NewsletterUnsubscribeRequest,
  NewsletterUnsubscribeResponse
} from './NewsletterAPIClient';

export { ClubsAPIClient, clubsAPIClient } from './ClubsAPIClient';
export type { Club } from '@/features/clubs/types/clubs';
export type { ClubsResponse, ClubsQueryParams } from './ClubsAPIClient';
