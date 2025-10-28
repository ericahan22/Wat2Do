import { BaseAPIClient } from './BaseAPIClient';

export interface NewsletterSubscribeRequest {
  email: string;
}

export interface NewsletterSubscribeResponse {
  message: string;
  success: boolean;
}

export interface NewsletterUnsubscribeRequest {
  email: string;
  token: string;
}

export interface NewsletterUnsubscribeResponse {
  message: string;
  success: boolean;
}

export class NewsletterAPIClient extends BaseAPIClient {
  constructor() {
    super();
  }

  async subscribe(data: NewsletterSubscribeRequest): Promise<NewsletterSubscribeResponse> {
    return this.post<NewsletterSubscribeResponse>('/api/newsletter/subscribe/', data);
  }

  async unsubscribe(data: NewsletterUnsubscribeRequest): Promise<NewsletterUnsubscribeResponse> {
    return this.post<NewsletterUnsubscribeResponse>('/api/newsletter/unsubscribe/', data);
  }

  async getUnsubscribeInfo(token: string): Promise<{
    already_unsubscribed: boolean;
    email: string;
    message: string;
    unsubscribed_at?: string;
  }> {
    return this.get(`/api/newsletter/unsubscribe/${token}`);
  }

  async submitUnsubscribe(token: string, data: {
    reason: string;
    feedback?: string;
  }): Promise<{
    message: string;
    email: string;
    unsubscribed_at: string;
  }> {
    return this.post(`/api/newsletter/unsubscribe/${token}`, data);
  }
}

// Export a default instance
export const newsletterAPIClient = new NewsletterAPIClient();
