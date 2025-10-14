import { useMutation } from "@tanstack/react-query";
import { API_BASE_URL } from '@/shared/constants/api';

interface SubscribeResponse {
  message: string;
  email: string;
}

interface SubscribeError {
  error: string;
}

const subscribeToNewsletter = async (email: string): Promise<SubscribeResponse> => {
  const response = await fetch(`${API_BASE_URL}/newsletter/subscribe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error((data as SubscribeError).error || "Something went wrong");
  }

  return data as SubscribeResponse;
};

export const useNewsletterSubscribe = () => {
  const mutation = useMutation({
    mutationFn: subscribeToNewsletter,
  });

  return {
    subscribe: mutation.mutate,
    ...mutation,
  };
};

