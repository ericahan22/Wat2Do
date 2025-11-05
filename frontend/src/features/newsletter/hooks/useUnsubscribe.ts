import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useApi } from '@/shared/hooks/useApi';
import NewsletterAPIClient from '@/shared/api/NewsletterAPIClient';

interface UnsubscribeData {
  already_unsubscribed: boolean;
  email: string;
  message: string;
  unsubscribed_at?: string;
}

interface UnsubscribeRequest {
  reason: string;
  feedback?: string;
}

interface UnsubscribeResponse {
  message: string;
  email: string;
  unsubscribed_at: string;
}


const fetchUnsubscribeInfo = async (token: string, newsletterAPI: NewsletterAPIClient): Promise<UnsubscribeData> => {
  return newsletterAPI.getUnsubscribeInfo(token);
};

const submitUnsubscribe = async (
  token: string, 
  data: UnsubscribeRequest,
  newsletterAPI: NewsletterAPIClient
): Promise<UnsubscribeResponse> => {
  return newsletterAPI.submitUnsubscribe(token, data);
};

export const useUnsubscribe = (token: string | undefined) => {
  const queryClient = useQueryClient();
  const { newsletterAPIClient } = useApi();

  // Query to fetch unsubscribe info
  const {
    data: unsubscribeInfo,
    isLoading,
    error: fetchError,
    isError: isFetchError,
  } = useQuery({
    queryKey: ['unsubscribe', token],
    queryFn: () => fetchUnsubscribeInfo(token!, newsletterAPIClient),
    enabled: !!token,
    retry: false,
  });

  // Mutation to submit unsubscribe
  const {
    mutate: submitUnsubscribeMutation,
    isPending: isSubmitting,
    isSuccess: isSubmitSuccess,
    error: submitError,
    isError: isSubmitError,
    data: submitData,
    reset: resetSubmit,
  } = useMutation({
    mutationFn: (data: UnsubscribeRequest) => submitUnsubscribe(token!, data, newsletterAPIClient),
    onSuccess: () => {
      // Invalidate and refetch the unsubscribe info
      queryClient.invalidateQueries({ queryKey: ['unsubscribe', token] });
    },
  });

  // Combined error state
  const error = fetchError || submitError;
  const isError = isFetchError || isSubmitError;

  const unsubscribe = (reason: string, feedback?: string) => {
    if (!token) {
      throw new Error('No unsubscribe token provided');
    }
    
    submitUnsubscribeMutation({ reason, feedback });
  };

  return {
    // Data
    unsubscribeInfo,
    submitData,
    
    // Loading states
    isLoading,
    isSubmitting,
    
    // Success states
    isSubmitSuccess,
    
    // Error states
    error,
    isError,
    
    // Actions
    unsubscribe,
    resetSubmit,
    
    // Computed states
    isAlreadyUnsubscribed: unsubscribeInfo?.already_unsubscribed ?? false,
    email: unsubscribeInfo?.email || submitData?.email,
    isReady: !isLoading && !isError && !!unsubscribeInfo,
  };
};

export type { UnsubscribeData, UnsubscribeRequest, UnsubscribeResponse };
