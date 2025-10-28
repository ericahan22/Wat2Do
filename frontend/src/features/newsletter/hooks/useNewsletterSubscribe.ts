import { useMutation } from "@tanstack/react-query";
import { newsletterAPIClient } from '@/shared/api';

export const useNewsletterSubscribe = () => {
  const mutation = useMutation({
    mutationFn: newsletterAPIClient.subscribe,
  });

  return {
    subscribe: mutation.mutate,
    ...mutation,
  };
};

