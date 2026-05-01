import BaseAPIClient from "./BaseAPIClient";

export interface PosterCampaign {
  id: string;
  label: string;
  destination_url: string | null;
  scan_count: number;
  needs_location: boolean;
  first_location: {
    latitude: number | null;
    longitude: number | null;
    accuracy_m: number | null;
    captured_at: string | null;
  };
  scan_url: string;
  qr_svg: string;
  created_at: string;
}

export interface CreatePosterCampaignRequest {
  label: string;
  destination_url?: string;
  base_url?: string;
}

export interface PosterScanStatus {
  id: string;
  destination_url: string | null;
  scan_count: number;
  needs_location: boolean;
}

export interface PosterScan {
  id: number;
  poster_id: string;
  scan_number: number;
  created_at: string;
  user_agent: string | null;
}

export interface RecordPosterScanRequest {
  latitude?: number;
  longitude?: number;
  accuracy_m?: number;
}

export interface RecordPosterScanResponse {
  id: string;
  scan_count: number;
  location_saved: boolean;
  destination_url: string | null;
}

class PosterAPIClient {
  constructor(private apiClient: BaseAPIClient) {}

  async createPosterCampaign(
    data: CreatePosterCampaignRequest
  ): Promise<PosterCampaign> {
    return this.apiClient.post("posters/admin/create/", data);
  }

  async listPosterCampaigns(): Promise<{ posters: PosterCampaign[] }> {
    return this.apiClient.get("posters/admin/");
  }

  async listPosterScans(): Promise<{ scans: PosterScan[] }> {
    return this.apiClient.get("posters/admin/scans/");
  }

  async getPosterScanStatus(posterId: string): Promise<PosterScanStatus> {
    return this.apiClient.get(`posters/${posterId}/status/`);
  }

  async recordPosterScan(
    posterId: string,
    data: RecordPosterScanRequest = {}
  ): Promise<RecordPosterScanResponse> {
    return this.apiClient.post(`posters/${posterId}/scan/`, data);
  }
}

export default PosterAPIClient;
