import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/shared/lib/api';
import { SubmittedClub } from '../types/clubs';

interface SubmitClubData {
  clubName: string;
  categories: string;
  clubPage: string;
  ig: string;
  discord: string;
  clubType: string;
}

export function useSubmitClub() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (data: SubmitClubData): Promise<SubmittedClub> => {
      const response = await apiRequest('/clubs/submit/', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit club');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch user club submissions
      queryClient.invalidateQueries({ queryKey: ['userClubSubmissions'] });
    },
  });

  return {
    submitClub: mutation.mutate,
    isLoading: mutation.isPending,
    error: mutation.error?.message || null,
  };
}
