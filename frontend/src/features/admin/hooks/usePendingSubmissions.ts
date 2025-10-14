import { useQuery } from '@tanstack/react-query';
import { useLocalStorage } from 'react-use';
import { SubmittedEvent } from '../../events/types/events';
import { SubmittedClub } from '../../clubs/types/clubs';
import { API_BASE_URL } from '@/shared/constants/api';

export function usePendingEventSubmissions() {
  const [authToken] = useLocalStorage<string>('authToken');

  const query = useQuery({
    queryKey: ['pendingEventSubmissions'],
    queryFn: async (): Promise<SubmittedEvent[]> => {
      if (!authToken) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE_URL}/events/submissions/pending/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch pending event submissions');
      }

      return response.json();
    },
    enabled: !!authToken,
  });

  return {
    submissions: query.data || [],
    isLoading: query.isLoading,
    error: query.error?.message || null,
    refetch: query.refetch,
  };
}

export function usePendingClubSubmissions() {
  const [authToken] = useLocalStorage<string>('authToken');

  const query = useQuery({
    queryKey: ['pendingClubSubmissions'],
    queryFn: async (): Promise<SubmittedClub[]> => {
      if (!authToken) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE_URL}/clubs/submissions/pending/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch pending club submissions');
      }

      return response.json();
    },
    enabled: !!authToken,
  });

  return {
    submissions: query.data || [],
    isLoading: query.isLoading,
    error: query.error?.message || null,
    refetch: query.refetch,
  };
}
