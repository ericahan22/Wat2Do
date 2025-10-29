import { useMutation } from "@tanstack/react-query";
import { useApi } from '@/shared/hooks/useApi';

export const useNewsletterSubscribe = () => {
  const { newsletter } = useApi();
  
  const mutation = useMutation({
    mutationFn: (data: Parameters<typeof newsletter.subscribe>[0]) => newsletter.subscribe(data),
  });

  return {
    subscribe: mutation.mutate,
    ...mutation,
  };
};

