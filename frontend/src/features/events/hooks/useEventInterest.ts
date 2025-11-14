import { useMutation, useQuery, useQueryClient, InfiniteData } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import { useApi } from "@/shared/hooks/useApi";
import type { EventsResponse } from "@/shared/api/EventsAPIClient";
import type { Event } from "@/features/events/types/events";

/**
 * Hook to get all event IDs the current user is interested in
 */
export function useMyInterestedEvents() {
  const { isSignedIn } = useAuth();
  const { eventsAPIClient } = useApi();

  return useQuery({
    queryKey: ["my-interested-events"],
    queryFn: async () => {
      const response = await eventsAPIClient.getMyInterestedEventIds();
      return new Set(response.event_ids); // Convert to Set for O(1) lookup
    },
    enabled: isSignedIn,
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
      await queryClient.cancelQueries({ queryKey: ["events"] });

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

      // Optimistically update event interest counts in events list (infinite query structure)
      queryClient.setQueriesData<InfiniteData<EventsResponse>>({ queryKey: ["events"] }, (oldData) => {
        if (!oldData?.pages) return oldData;
        
        return {
          ...oldData,
          pages: oldData.pages.map((page: EventsResponse) => ({
            ...page,
            results: page.results.map((event: Event) => {
              if (event.id === eventId) {
                const delta = nextInterested ? 1 : -1;
                return {
                  ...event,
                  interest_count: Math.max(0, (event.interest_count || 0) + delta),
                };
              }
              return event;
            }),
          })),
        };
      });

      return { prevInterestedEvents };
    },
    onSuccess: (response) => {
      // Update the event's interest count with the actual server value (infinite query structure)
      queryClient.setQueriesData<InfiniteData<EventsResponse>>({ queryKey: ["events"] }, (oldData) => {
        if (!oldData?.pages) return oldData;
        
        return {
          ...oldData,
          pages: oldData.pages.map((page: EventsResponse) => ({
            ...page,
            results: page.results.map((event: Event) => {
              if (event.id === eventId) {
                return {
                  ...event,
                  interest_count: response.interest_count,
                };
              }
              return event;
            }),
          })),
        };
      });
    },
    onError: (_err, nextInterested, context) => {
      // Rollback optimistic updates on error
      if (context?.prevInterestedEvents) {
        queryClient.setQueryData(["my-interested-events"], context.prevInterestedEvents);
      }
      
      // Rollback event interest count (infinite query structure)
      queryClient.setQueriesData<InfiniteData<EventsResponse>>({ queryKey: ["events"] }, (oldData) => {
        if (!oldData?.pages) return oldData;
        
        return {
          ...oldData,
          pages: oldData.pages.map((page: EventsResponse) => ({
            ...page,
            results: page.results.map((event: Event) => {
              if (event.id === eventId) {
                const delta = nextInterested ? -1 : 1; // Reverse the optimistic update
                return {
                  ...event,
                  interest_count: Math.max(0, (event.interest_count || 0) + delta),
                };
              }
              return event;
            }),
          })),
        };
      });
    },
    onSettled: () => {
      // Only reconcile the interested events list (lightweight query)
      // Skip refetching the expensive events list since we updated it directly
      queryClient.invalidateQueries({ queryKey: ["my-interested-events"] });
    },
  });
}

