import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useApi } from '@/shared/hooks/useApi';

export const useEventSubmission = () => {
  const queryClient = useQueryClient();
  const { eventsAPIClient } = useApi();

  const submitEventMutation = useMutation({
    mutationFn: (data: Parameters<typeof eventsAPIClient.submitEvent>[0]) => eventsAPIClient.submitEvent(data),
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
