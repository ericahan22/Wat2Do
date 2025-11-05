// Base API Client - Uses constructor pattern with getAuthToken
export { default as BaseAPIClient } from './BaseAPIClient';

// Feature API Clients - Clean class pattern!
export { default as EventsAPIClient } from './EventsAPIClient';
export type { Event, EventSubmission, SubmissionFormData, EventsQueryParams, EventSubmissionResponse } from './EventsAPIClient';

export { default as AdminAPIClient } from './AdminAPIClient';
export type { 
  PromoteEventRequest, 
  UpdatePromotionRequest, 
  PromoteEventResponse,
  UpdatePromotionResponse,
  UnpromoteEventResponse,
  PromotedEventsResponse,
  PromotionStatusResponse
} from '@/features/admin/types/promotion';

export { default as NewsletterAPIClient } from './NewsletterAPIClient';
export type { 
  NewsletterSubscribeRequest, 
  NewsletterSubscribeResponse,
  NewsletterUnsubscribeRequest,
  NewsletterUnsubscribeResponse
} from './NewsletterAPIClient';

export { default as ClubsAPIClient } from './ClubsAPIClient';
export type { Club } from '@/features/clubs/types/clubs';
export type { ClubsResponse, ClubsQueryParams } from './ClubsAPIClient';
