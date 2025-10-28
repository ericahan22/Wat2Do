import { useMutation, useQueryClient } from '@tanstack/react-query';
import { eventsAPIClient } from '@/shared/api';

export const useEventSubmission = () => {
  const queryClient = useQueryClient();

  const submitEventMutation = useMutation({
    mutationFn: eventsAPIClient.submitEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-submissions'] });
    },
  });

  return {
    submitEvent: submitEventMutation.mutate,
    isLoading: submitEventMutation.isPending,
    isSuccess: submitEventMutation.isSuccess,
    isError: submitEventMutation.isError,
    error: submitEventMutation.error,
  };
};
