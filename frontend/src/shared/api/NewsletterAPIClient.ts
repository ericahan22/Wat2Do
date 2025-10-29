export interface NewsletterSubscribeRequest {
  email: string;
}

export interface NewsletterSubscribeResponse {
  message: string;
  email: string;
  unsubscribe_token: string;
}

export interface NewsletterUnsubscribeRequest {
  token: string;
}

export interface NewsletterUnsubscribeResponse {
  message: string;
  email: string;
  unsubscribed_at: string;
}

/**
 * Newsletter API Client - Clean class pattern!
 * Takes BaseAPIClient as constructor parameter
 */
class NewsletterAPIClient {
  /**
   * @param {BaseAPIClient} apiClient A pre-configured instance of the base API client.
   */
  constructor(private apiClient: any) {}

  /**
   * Subscribes to newsletter.
   * Corresponds to a POST request to /api/newsletter/subscribe/
   */
  async subscribe(data: NewsletterSubscribeRequest): Promise<NewsletterSubscribeResponse> {
    return this.apiClient.post('newsletter/subscribe/', data);
  }

  /**
   * Unsubscribes from newsletter.
   * Corresponds to a POST request to /api/newsletter/unsubscribe/
   */
  async unsubscribe(data: NewsletterUnsubscribeRequest): Promise<NewsletterUnsubscribeResponse> {
    return this.apiClient.post('newsletter/unsubscribe/', data);
  }

  /**
   * Gets subscription status.
   * Corresponds to a GET request to /api/newsletter/status/
   */
  async getSubscriptionStatus(email: string): Promise<{ subscribed: boolean; email: string }> {
    return this.apiClient.get(`newsletter/status/?email=${encodeURIComponent(email)}`);
  }

  /**
   * Resubscribes to newsletter.
   * Corresponds to a POST request to /api/newsletter/resubscribe/
   */
  async resubscribe(email: string): Promise<{ message: string; email: string }> {
    return this.apiClient.post('newsletter/resubscribe/', { email });
  }
}

export default NewsletterAPIClient;