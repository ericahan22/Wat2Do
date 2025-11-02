import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { useApi } from "@/shared/hooks/useApi";
import type { EventSubmission } from "@/features/events/types/submission";

type ReviewAction = "approve" | "reject";

export function useSubmissionsReview() {
  const queryClient = useQueryClient();
  const { eventsAPIClient } = useApi();
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<number | null>(null);
  const [editedExtractedData, setEditedExtractedData] = useState<string>("");
  const [parseError, setParseError] = useState<string | null>(null);

  const submissionsQuery = useQuery<EventSubmission[]>({
    queryKey: ["admin", "submissions"],
    queryFn: () => eventsAPIClient.getSubmissions(),
  });

  const selectedSubmission = submissionsQuery.data?.find((s) => s.id === selectedSubmissionId) ?? null;

  const processMutation = useMutation({
    mutationFn: (submissionId: number) => eventsAPIClient.processSubmission(submissionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "submissions"] });
    },
  });

  const reviewMutation = useMutation({
    mutationFn: ({
      submissionId,
      action,
      notes,
      extractedData,
    }: {
      submissionId: number;
      action: ReviewAction;
      notes?: string;
      extractedData?: Record<string, unknown>;
    }) => eventsAPIClient.reviewSubmission(submissionId, action, notes, extractedData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "submissions"] });
      setSelectedSubmissionId(null);
    },
  });

  // Update edited data when selected submission changes
  useEffect(() => {
    if (selectedSubmission?.extracted_data) {
      setEditedExtractedData(JSON.stringify(selectedSubmission.extracted_data, null, 2));
      setParseError(null);
    } else {
      setEditedExtractedData("");
      setParseError(null);
    }
  }, [selectedSubmission]);

  const handleExtractedDataChange = (value: string) => {
    setEditedExtractedData(value);
    // Try to parse and validate JSON
    try {
      JSON.parse(value);
      setParseError(null);
    } catch {
      setParseError("Invalid JSON");
    }
  };

  const handleReview = async (action: ReviewAction) => {
    if (!selectedSubmission) return;

    let extractedData: Record<string, unknown> | undefined = undefined;
    if (action === "approve" && editedExtractedData) {
      try {
        extractedData = JSON.parse(editedExtractedData);
      } catch {
        setParseError("Invalid JSON - cannot approve");
        return;
      }
    }

    await reviewMutation.mutateAsync({
      submissionId: selectedSubmission.id,
      action,
      extractedData,
    });
  };

  return {
    submissions: submissionsQuery.data ?? [],
    submissionsLoading: submissionsQuery.isLoading,
    refetchSubmissions: submissionsQuery.refetch,

    processSubmission: processMutation.mutateAsync,
    isProcessing: processMutation.isPending,

    reviewSubmission: reviewMutation.mutateAsync,
    handleReview,
    isReviewing: reviewMutation.isPending,

    selectedSubmission,
    setSelectedSubmission: (submission: EventSubmission | null) =>
      setSelectedSubmissionId(submission?.id ?? null),

    editedExtractedData,
    handleExtractedDataChange,
    parseError,
  };
}


