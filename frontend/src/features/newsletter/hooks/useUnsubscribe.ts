import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '@/shared/constants/api';

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


const fetchUnsubscribeInfo = async (token: string): Promise<UnsubscribeData> => {
  const response = await fetch(`${API_BASE_URL}/newsletter/unsubscribe/${token}`);
  
  if (!response.ok) {
    // Check if response is JSON before trying to parse
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to load unsubscribe information');
    } else {
      // Handle non-JSON responses (like HTML 404 pages)
      if (response.status === 404) {
        throw new Error('Invalid unsubscribe token');
      }
      throw new Error(`Server error: ${response.status}`);
    }
  }
  
  return response.json();
};

const submitUnsubscribe = async (
  token: string, 
  data: UnsubscribeRequest
): Promise<UnsubscribeResponse> => {
  const response = await fetch(`${API_BASE_URL}/newsletter/unsubscribe/${token}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    // Check if response is JSON before trying to parse
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to unsubscribe');
    } else {
      // Handle non-JSON responses
      if (response.status === 404) {
        throw new Error('Invalid unsubscribe token');
      }
      throw new Error(`Server error: ${response.status}`);
    }
  }

  return response.json();
};

export const useUnsubscribe = (token: string | undefined) => {
  const queryClient = useQueryClient();

  // Query to fetch unsubscribe info
  const {
    data: unsubscribeInfo,
    isLoading,
    error: fetchError,
    isError: isFetchError,
  } = useQuery({
    queryKey: ['unsubscribe', token],
    queryFn: () => fetchUnsubscribeInfo(token!),
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
    mutationFn: (data: UnsubscribeRequest) => submitUnsubscribe(token!, data),
    onSuccess: () => {
      // Invalidate and refetch the unsubscribe info
      queryClient.invalidateQueries({ queryKey: ['unsubscribe', token] });
    },
  });

  // Combined error state
  const error = fetchError || submitError;
  const isError = isFetchError || isSubmitError;

  // Helper function to submit unsubscribe
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
