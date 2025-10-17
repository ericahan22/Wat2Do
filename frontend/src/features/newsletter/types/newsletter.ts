export interface NewsletterSubscriber {
  id: string;
  email: string;
  subscribed_at: string;
  unsubscribe_token: string;
}

export interface NewsletterSubscribeRequest {
  email: string;
}

export interface NewsletterSubscribeResponse {
  message: string;
  subscriber: NewsletterSubscriber;
}

export interface UnsubscribeRequest {
  token: string;
  reason?: string;
}

export interface UnsubscribeResponse {
  message: string;
}
