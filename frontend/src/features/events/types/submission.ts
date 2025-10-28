export interface EventSubmission {
  id: number;
  screenshot_url: string;
  source_url: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_at: string;
  reviewed_at: string | null;
  admin_notes: string;
  extracted_data: Record<string, unknown> | null;
  created_event_id: number | null;
}

export interface SubmitEventData {
  screenshot: File;
  source_url: string;
}
