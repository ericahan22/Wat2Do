import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useApi } from '@/shared/hooks/useApi';
import { useAuth } from '@clerk/clerk-react';
import type { EventSubmission } from '@/features/events/types/submission';

export const useUserSubmissions = () => {
  const { isSignedIn, userId } = useAuth();
  const { eventsAPIClient } = useApi();
  const queryClient = useQueryClient();

  // Fetch current user's submissions
  const submissionsQuery = useQuery<EventSubmission[]>({
    queryKey: ['user-submissions', userId],
    queryFn: () => eventsAPIClient.getUserSubmissions(),
    enabled: isSignedIn && !!userId,
    staleTime: 30 * 1000,  
    gcTime: 5 * 60 * 1000,  
  });

  // Delete a submission owned by the current user
  const { mutate: removeSubmission, isPending: isDeleting } = useMutation({
    mutationFn: (submissionId: number) => eventsAPIClient.deleteSubmission(submissionId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['user-submissions'] });
    },
  });

  return {
    ...submissionsQuery,
    removeSubmission,
    isDeleting,
  };
};
