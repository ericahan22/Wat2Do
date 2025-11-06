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
  limit?: number;
  cursor?: string;
  all?: boolean; // For calendar view - returns all events without pagination
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
   * Extract event data from screenshot.
   * Corresponds to a POST request to /api/events/extract/
   */
  async extractEventFromScreenshot(screenshot: File): Promise<{
    screenshot_url: string;
    extracted_data: any;
    all_extracted: any[];
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
      throw new Error(error.error || 'Failed to extract event data');
    }
    
    return response.json();
  }

  async submitEvent(formData: SubmissionFormData): Promise<EventSubmissionResponse> {
    const payload = {
      screenshot_url: formData.screenshot_url,
      extracted_data: formData.extracted_data,
    };
    
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
        if (typeof errBody?.error === 'string' && errBody.error.trim()) {
          message = errBody.error;
        } else if (typeof errBody?.message === 'string' && errBody.message.trim()) {
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
    adminNotes?: string,
    extractedData?: Record<string, unknown>
  ): Promise<{ message: string }> {
    return this.apiClient.post(
      `events/submissions/${submissionId}/review/`,
      { action, admin_notes: adminNotes, extracted_data: extractedData }
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
   * Corresponds to a GET request to /api/events/export/ics/
   * Special handling for file download
   */
  async exportEventsICS(params: EventsQueryParams = {}): Promise<Blob> {
    const queryString = buildQueryString(params);
    const endpoint = queryString ? `events/export/ics/?${queryString}` : 'events/export/ics/';
    
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
   * Gets RSS feed for events.
   * Corresponds to a GET request to /api/events/rss/
   * Special handling for XML response
   */
  async getRSSFeed(): Promise<string> {
    const token = await this.apiClient.getAuthToken();
    const headers: HeadersInit = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/events/rss/`, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.text();
  }

  /**
   * Gets promoted events.
   * Corresponds to a GET request to /api/events/promoted/
   */
  async getPromotedEvents(): Promise<Event[]> {
    return this.apiClient.get('events/promoted/');
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
   * Deletes an event and all its related data (admin only).
   * Corresponds to a DELETE request to /api/events/{id}/delete/
   */
  async deleteEvent(eventId: number): Promise<{ message: string }> {
    return this.apiClient.delete(`events/${eventId}/delete/`);
  }
}

export default EventsAPIClient;