import type { EventSubmission } from '@/features/events/types/submission';
import type { Event } from '@/features/events/types/events';
import type { SubmissionFormData } from '@/features/events/schemas/submissionSchema';
import BaseAPIClient from '@/shared/api/BaseAPIClient';

// Re-export types for external use
export type { Event, EventSubmission, SubmissionFormData };

export interface EventsQueryParams {
  search?: string;
  categories?: string;
  dtstart_utc?: string;
  added_at?: string;
  cursor?: string;
  all?: boolean; // For calendar view - returns all events without pagination
  ids?: string; // Comma-separated list of event IDs for export/calendar URLs
}

export interface EventSubmissionResponse {
  id: number;
  message: string;
}

export interface EventSubmissionsResponse {
  submissions: EventSubmission[];
}

export interface EventsResponse {
  results: Event[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

// Helper function to build query string (DRY principle)
function buildQueryString(params: EventsQueryParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  return searchParams.toString();
}

/**
 * Events API Client - Clean class pattern!
 * Takes BaseAPIClient as constructor parameter
 */
class EventsAPIClient {
  /**
   * @param {BaseAPIClient} apiClient A pre-configured instance of the base API client.
   */
  constructor(private apiClient: BaseAPIClient) {}

  /**
   * Fetches events from the backend with cursor-based pagination.
   * Corresponds to a GET request to /api/events/
   */
  async getEvents(params: EventsQueryParams = {}): Promise<EventsResponse> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `events/?${queryString}` : 'events/';
    return this.apiClient.get(endpoint);
  }

  /**
   * Fetches a single event by its ID.
   * Corresponds to a GET request to /api/events/{id}/
   */
  async getEvent(eventId: number): Promise<Event> {
    return this.apiClient.get(`events/${eventId}/`);
  }

  /**
   * Gets user's event submissions.
   * Corresponds to a GET request to /api/events/my-submissions/
   */
  async getUserSubmissions(): Promise<EventSubmission[]> {
    return this.apiClient.get('events/my-submissions/');
  }

  /**
   * Gets all event submissions (admin).
   * Corresponds to a GET request to /api/events/submissions/
   */
  async getSubmissions(): Promise<EventSubmission[]> {
    return this.apiClient.get('events/submissions/');
  }

  /**
   * Submits a new event for review.
   * Corresponds to a POST request to /api/events/submit/
   * Special handling for FormData (file uploads)
   */
  /**
   * Extract event data from image.
   * Corresponds to a POST request to /api/events/extract/
   */
  async extractEventFromScreenshot(screenshot: File): Promise<{
    source_image_url: string;
    title: string;
    description?: string;
    location: string;
    price?: number;
    food?: string;
    registration: boolean;
    occurrences: Array<{ dtstart_utc: string; dtend_utc?: string; tz?: string }>;
    all_extracted: unknown[];
  }> {
    const dataForm = new FormData();
    dataForm.append('screenshot', screenshot);
    
    const token = await this.apiClient.getAuthToken();
    const headers: HeadersInit = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/events/extract/`, {
      method: 'POST',
      headers,
      body: dataForm,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to extract event data');
    }
    
    return response.json();
  }

  async submitEvent(formData: SubmissionFormData): Promise<EventSubmissionResponse> {
    // Payload is now flat - all event fields at top level
    const payload = { ...formData };
    
    // For JSON payload
    const token = await this.apiClient.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/events/submit/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      let message = `Submission failed (status ${response.status})`;
      try {
        const errBody = await response.json();
        if (typeof errBody?.message === 'string' && errBody.message.trim()) {
          message = errBody.message;
        }
      } catch {
        // ignore JSON parse errors
      }
      throw new Error(message);
    }
    
    return response.json();
  }

  /**
   * Reviews a submission (admin).
   * Corresponds to a POST request to /api/events/submissions/{id}/review/
   */
  async reviewSubmission(
    submissionId: number,
    action: 'approve' | 'reject',
    eventData?: Record<string, unknown>
  ): Promise<{ message: string }> {
    // Event data is now passed flat at top level (not nested)
    const payload: Record<string, unknown> = { action };
    if (eventData) {
      Object.assign(payload, eventData);
    }
    return this.apiClient.post(
      `events/submissions/${submissionId}/review/`,
      payload
    );
  }

  /**
   * Deletes a user's own submission.
   * Corresponds to a DELETE request to /api/events/submissions/{id}/
   */
  async deleteSubmission(submissionId: number): Promise<{ message: string }> {
    return this.apiClient.delete(`events/submissions/${submissionId}/`);
  }

  /**
   * Exports events as ICS file.
   * Corresponds to a GET request to /api/events/export.ics
   * Special handling for file download
   */
  async exportEventsICS(params: EventsQueryParams = {}): Promise<Blob> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `events/export.ics?${queryString}` : 'events/export.ics';
    
    const token = await this.apiClient.getAuthToken();
    const headers: HeadersInit = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/${endpoint}`, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.blob();
  }

  /**
   * Gets Google Calendar URLs for events.
   * Corresponds to a GET request to /api/events/google-calendar-urls/
   */
  async getGoogleCalendarUrls(params: EventsQueryParams = {}): Promise<{ urls: string[] }> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `events/google-calendar-urls/?${queryString}` : 'events/google-calendar-urls/';
    return this.apiClient.get(endpoint);
  }


  /**
   * Gets the current user's interested event IDs.
   * Corresponds to a GET request to /api/events/my-interests/
   */
  async getMyInterestedEventIds(): Promise<{ event_ids: number[] }> {
    return this.apiClient.get('events/my-interests/');
  }

  /**
   * Mark interest in an event.
   * Corresponds to a POST request to /api/events/{id}/interest/mark/
   */
  async markEventInterest(eventId: number): Promise<{ message: string; interested: boolean; interest_count: number }> {
    return this.apiClient.post(`events/${eventId}/interest/mark/`);
  }

  /**
   * Unmark interest in an event.
   * Corresponds to a DELETE request to /api/events/{id}/interest/unmark/
   */
  async unmarkEventInterest(eventId: number): Promise<{ message: string; interested: boolean; interest_count: number }> {
    return this.apiClient.delete(`events/${eventId}/interest/unmark/`);
  }

  /**
   * Updates an event (submitter or admin only).
   * Corresponds to a PUT request to /api/events/{id}/update/
   */
  async updateEvent(eventId: number, eventData: Record<string, unknown>): Promise<{ message: string; event_id: number }> {
    return this.apiClient.put(`events/${eventId}/update/`, { event_data: eventData });
  }

  /**
   * Deletes an event and all its related data (admin only).
   * Corresponds to a DELETE request to /api/events/{id}/delete/
   */
  async deleteEvent(eventId: number): Promise<{ message: string }> {
    return this.apiClient.delete(`events/${eventId}/delete/`);
  }
}

export default EventsAPIClient;