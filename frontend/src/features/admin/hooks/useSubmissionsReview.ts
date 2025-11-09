import { useQuery } from "@tanstack/react-query";
import { useApi } from "@/shared/hooks/useApi";

export function useSubmissionsReview() {
  const { eventsAPIClient } = useApi();

  const submissionsQuery = useQuery({
    queryKey: ["admin", "submissions"],
    queryFn: () => eventsAPIClient.getSubmissions(),
  });

  return {
    submissions: submissionsQuery.data ?? [],
    submissionsLoading: submissionsQuery.isLoading,
    refetchSubmissions: submissionsQuery.refetch,
  };
}


