import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/shared/hooks/useApi";
import { useAuthState } from "@/features/auth/hooks/useAuthState";

/**
 * Hook to get all event IDs the current user is interested in
 */
export function useMyInterestedEvents() {
  const { isLoading, isSignedIn } = useAuthState();
  const { eventsAPIClient } = useApi();

  return useQuery({
    queryKey: ["my-interested-events"],
    queryFn: async () => {
      const response = await eventsAPIClient.getMyInterestedEventIds();
      return new Set(response.event_ids); // Convert to Set for O(1) lookup
    },
    enabled: !isLoading && isSignedIn,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
    meta: {
      skipErrorToast: true,
    },
  });
}

/**
 * Hook to toggle interest for a specific event with optimistic updates
 */
export function useToggleEventInterest(eventId: number) {
  const { eventsAPIClient } = useApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (nextInterested: boolean) => {
      if (nextInterested) {
        return eventsAPIClient.markEventInterest(eventId);
      } else {
        return eventsAPIClient.unmarkEventInterest(eventId);
      }
    },
    onMutate: async (nextInterested: boolean) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["my-interested-events"] });

      // Snapshot the previous value
      const prevInterestedEvents = queryClient.getQueryData<Set<number>>(["my-interested-events"]);

      // Optimistically update the interested events set
      queryClient.setQueryData<Set<number>>(["my-interested-events"], (old) => {
        if (!old) return new Set(nextInterested ? [eventId] : []);
        const newSet = new Set(old);
        if (nextInterested) {
          newSet.add(eventId);
        } else {
          newSet.delete(eventId);
        }
        return newSet;
      });

      return { prevInterestedEvents };
    },
    onError: (_err, _nextInterested, context) => {
      // Rollback optimistic updates on error
      if (context?.prevInterestedEvents) {
        queryClient.setQueryData(["my-interested-events"], context.prevInterestedEvents);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["my-interested-events"] });
    },
  });
}
