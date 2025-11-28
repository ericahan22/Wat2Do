import BaseAPIClient from './BaseAPIClient';

export interface School {
  slug: string;
  name: string;
  domains: string[];
}

export interface SchoolsResponse {
  schools: School[];
}

export interface JoinWaitlistRequest {
  email: string;
}

export interface JoinWaitlistResponse {
  message: string;
  email: string;
  school: string;
}

export interface WaitlistErrorResponse {
  error: string;
}

class WaitlistAPIClient {
  constructor(private apiClient: BaseAPIClient) {}

  async getSchools(): Promise<SchoolsResponse> {
    return this.apiClient.get('waitlist/schools/');
  }

  async getSchoolInfo(schoolSlug: string): Promise<School> {
    return this.apiClient.get(`waitlist/${schoolSlug}/`);
  }

  async joinWaitlist(schoolSlug: string, data: JoinWaitlistRequest): Promise<JoinWaitlistResponse> {
    return this.apiClient.post(`waitlist/${schoolSlug}/join/`, data);
  }
}

export default WaitlistAPIClient;
