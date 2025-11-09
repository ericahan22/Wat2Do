export interface EventSubmission {
  id: number;
  source_image_url: string | null;
  status: 'pending' | 'approved' | 'rejected';
  submitted_at: string;
  event_title: string | null;
  event_id: number;
  submitted_by?: string;
  reviewed_at?: string | null;
}

export interface SubmitEventData {
  screenshot: File;
  source_url: string;
}
