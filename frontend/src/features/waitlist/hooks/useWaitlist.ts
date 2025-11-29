import { useQuery, useMutation } from '@tanstack/react-query';
import { useApi } from '@/shared/hooks/useApi';
import type { School, JoinWaitlistResponse } from '@/shared/api/WaitlistAPIClient';

export const useWaitlist = (schoolSlug: string | undefined) => {
  const { waitlistAPIClient } = useApi();

  const {
    data: schoolInfo,
    isLoading,
    error: fetchError,
    isError: isFetchError,
  } = useQuery<School, Error>({
    queryKey: ['waitlist-school', schoolSlug],
    queryFn: () => waitlistAPIClient.getSchoolInfo(schoolSlug!),
    enabled: !!schoolSlug,
    retry: false,
  });

  const {
    mutate: joinWaitlistMutation,
    isPending: isSubmitting,
    isSuccess: isSubmitSuccess,
    error: submitError,
    isError: isSubmitError,
    data: submitData,
    reset: resetSubmit,
  } = useMutation<JoinWaitlistResponse, Error, string>({
    mutationFn: (email: string) => waitlistAPIClient.joinWaitlist(schoolSlug!, { email }),
    meta: {
      skipErrorToast: true,
    },
  });

  const joinWaitlist = (email: string) => {
    if (!schoolSlug) {
      throw new Error('No school slug provided');
    }
    joinWaitlistMutation(email);
  };

  // Get error message from the Error object
  const getErrorMessage = (): string | null => {
    if (!submitError) return null;
    return submitError.message;
  };

  return {
    schoolInfo,
    submitData,
    isLoading,
    isSubmitting,
    isSubmitSuccess,
    fetchError,
    submitError,
    isFetchError,
    isSubmitError,
    joinWaitlist,
    resetSubmit,
    isReady: !isLoading && !isFetchError && !!schoolInfo,
    errorMessage: getErrorMessage(),
  };
};
