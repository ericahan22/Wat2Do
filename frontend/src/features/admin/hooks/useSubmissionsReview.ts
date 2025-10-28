import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { eventsAPIClient } from "@/shared/api";
import type { EventSubmission } from "@/features/events/types/submission";

type ReviewAction = "approve" | "reject";

export function useSubmissionsReview() {
  const queryClient = useQueryClient();

  // List submissions (admin scope)
  const submissionsQuery = useQuery<EventSubmission[]>({
    queryKey: ["admin", "submissions"],
    queryFn: eventsAPIClient.getSubmissions,
  });

  // Ensure freshest data on mount
  useEffect(() => {
    submissionsQuery.refetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Process submission (extract event data)
  const processMutation = useMutation({
    mutationFn: (submissionId: number) => eventsAPIClient.processSubmission(submissionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "submissions"] });
    },
  });

  // Review submission (approve/reject)
  const reviewMutation = useMutation({
    mutationFn: ({ submissionId, action, notes }: { submissionId: number; action: ReviewAction; notes?: string }) =>
      eventsAPIClient.reviewSubmission(submissionId, action, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "submissions"] });
    },
  });

  return {
    // Data
    submissions: submissionsQuery.data ?? [],
    submissionsLoading: submissionsQuery.isLoading,
    submissionsError: submissionsQuery.error as unknown,
    refetchSubmissions: submissionsQuery.refetch,

    // Actions
    processSubmission: processMutation.mutateAsync,
    isProcessing: processMutation.isPending,
    processError: processMutation.error,

    reviewSubmission: reviewMutation.mutateAsync,
    isReviewing: reviewMutation.isPending,
    reviewError: reviewMutation.error,
  };
}


