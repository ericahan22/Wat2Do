import { useMutation } from "@tanstack/react-query";
import { useApi } from '@/shared/hooks/useApi';
import type { NewsletterSubscribeRequest, NewsletterSubscribeResponse } from '@/shared/api/NewsletterAPIClient';

export const useNewsletterSubscribe = () => {
  const { newsletterAPIClient } = useApi();
  
  const mutation = useMutation<NewsletterSubscribeResponse, unknown, NewsletterSubscribeRequest>({
    mutationFn: (data) => newsletterAPIClient.subscribe(data),
  });

  return {
    subscribe: mutation.mutate,
    ...mutation,
  };
};

