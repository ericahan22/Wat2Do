import { BaseAPIClient } from './BaseAPIClient';
import type { EventSubmission } from '@/features/events/types/submission';
import type { Event } from '@/features/events/types/events';
import type { SubmissionFormData } from '@/features/events/schemas/submissionSchema';

// Re-export types for external use
export type { Event, EventSubmission, SubmissionFormData };

export interface EventsQueryParams {
  search?: string;
  dtstart_utc?: string;
  added_at?: string;
  limit?: number;
  offset?: number;
}

export interface EventSubmissionResponse {
  id: number;
  message: string;
}

export interface EventSubmissionsResponse {
  submissions: EventSubmission[];
}

export class EventsAPIClient extends BaseAPIClient {
  constructor() {
    super();
  }

  async getEvents(params: EventsQueryParams = {}): Promise<Event[]> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/api/events/?${queryString}` : '/api/events/';
    
    return this.get<Event[]>(endpoint);
  }

  async getEvent(eventId: number): Promise<Event> {
    return this.get<Event>(`/api/events/${eventId}/`);
  }

  async submitEvent(formData: SubmissionFormData): Promise<EventSubmissionResponse> {
    const data = new FormData();
    data.append('screenshot', formData.screenshot);
    data.append('source_url', formData.source_url);

    return this.post<EventSubmissionResponse>('/api/events/submit/', data);
  }

  async getUserSubmissions(): Promise<EventSubmission[]> {
    return this.get<EventSubmission[]>('/api/events/my-submissions/');
  }

  async getSubmissions(): Promise<EventSubmission[]> {
    return this.get<EventSubmission[]>('/api/events/submissions/');
  }

  async processSubmission(submissionId: number): Promise<{ message: string }> {
    return this.post<{ message: string }>(`/api/events/submissions/${submissionId}/process/`);
  }

  async reviewSubmission(
    submissionId: number, 
    action: 'approve' | 'reject',
    adminNotes?: string
  ): Promise<{ message: string }> {
    return this.post<{ message: string }>(`/api/events/submissions/${submissionId}/review/`, {
      action,
      admin_notes: adminNotes,
    });
  }

  async exportEventsICS(params: EventsQueryParams = {}): Promise<Blob> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/api/events/export/ics/?${queryString}` : '/api/events/export/ics/';
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to export events');
    }

    return response.blob();
  }

  async getGoogleCalendarUrls(params: EventsQueryParams = {}): Promise<{ urls: string[] }> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/api/events/google-calendar-urls/?${queryString}` : '/api/events/google-calendar-urls/';
    
    return this.get<{ urls: string[] }>(endpoint);
  }

  async getRSSFeed(): Promise<string> {
    const response = await fetch(`${this.baseURL}/api/events/rss/`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to get RSS feed');
    }

    return response.text();
  }

  async getPromotedEvents(): Promise<Event[]> {
    return this.get<Event[]>('/api/events/promoted/');
  }
}

// Export a default instance
export const eventsAPIClient = new EventsAPIClient();
