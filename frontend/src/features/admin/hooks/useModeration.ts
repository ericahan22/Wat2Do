import { API_BASE_URL } from '@/shared/constants/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocalStorage } from 'react-use';  

export function useEventModeration() {
  const queryClient = useQueryClient();
  const [authToken] = useLocalStorage<string>('authToken');

  const mutation = useMutation({
    mutationFn: async ({ eventId, status, rejectionReason }: { 
      eventId: number; 
      status: 'approved' | 'rejected'; 
      rejectionReason?: string 
    }) => {
      if (!authToken) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE_URL}/events/submissions/${eventId}/moderate/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authToken}`,
        },
        body: JSON.stringify({
          status,
          rejection_reason: rejectionReason,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to moderate event');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch pending submissions
      queryClient.invalidateQueries({ queryKey: ['pendingEventSubmissions'] });
    },
  });

  return {
    moderateEvent: mutation.mutate,
    isLoading: mutation.isPending,
    error: mutation.error?.message || null,
  };
}

export function useClubModeration() {
  const queryClient = useQueryClient();
  const [authToken] = useLocalStorage<string>('authToken');

  const mutation = useMutation({
    mutationFn: async ({ clubId, status, rejectionReason }: { 
      clubId: number; 
      status: 'approved' | 'rejected'; 
      rejectionReason?: string 
    }) => {
      if (!authToken) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE_URL}/clubs/submissions/${clubId}/moderate/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authToken}`,
        },
        body: JSON.stringify({
          status,
          rejection_reason: rejectionReason,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to moderate club');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch pending submissions
      queryClient.invalidateQueries({ queryKey: ['pendingClubSubmissions'] });
    },
  });

  return {
    moderateClub: mutation.mutate,
    isLoading: mutation.isPending,
    error: mutation.error?.message || null,
  };
}
