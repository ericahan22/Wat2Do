import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/shared/hooks/useApi";
import type {
  PromoteEventRequest,
  UpdatePromotionRequest,
} from "@/features/admin/types/promotion";

/**
 * Hook for managing event promotions using React Query
 * Requires admin authentication token
 * 
 * Supports separate EventPromotion table (Option 2)
 */
export function useEventPromotion() {
  const queryClient = useQueryClient();
  const { adminAPIClient } = useApi();

  // Mutations
  const promoteMutation = useMutation({
    mutationFn: ({ eventId, data }: { eventId: string; data: PromoteEventRequest }) =>
      adminAPIClient.promoteEvent(eventId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "promotion-status"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ eventId, data }: { eventId: string; data: UpdatePromotionRequest }) =>
      adminAPIClient.updatePromotion(eventId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "promotion-status"] });
    },
  });

  const unpromoteMutation = useMutation({
    mutationFn: (eventId: string) => adminAPIClient.unpromoteEvent(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "promotion-status"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (eventId: string) => adminAPIClient.deletePromotion(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "promotion-status"] });
    },
  });

  // Queries
  const promotedEventsQuery = useQuery({
    queryKey: ["admin", "promoted-events"],
    queryFn: () => adminAPIClient.getPromotedEvents(),
  });

  const getPromotionStatusQueryOptions = (eventId: string) => ({
    queryKey: ["admin", "promotion-status", eventId],
    queryFn: () => adminAPIClient.getPromotionStatus(eventId),
    enabled: !!eventId,
  });

  return {
    // Mutations
    promoteEvent: (eventId: string, data: PromoteEventRequest = {}) =>
      promoteMutation.mutateAsync({ eventId, data }),
    updatePromotion: (eventId: string, data: UpdatePromotionRequest) =>
      updateMutation.mutateAsync({ eventId, data }),
    unpromoteEvent: (eventId: string) => unpromoteMutation.mutateAsync(eventId),
    deletePromotion: (eventId: string) => deleteMutation.mutateAsync(eventId),

    // Loading states
    isPromoting: promoteMutation.isPending,
    isUpdating: updateMutation.isPending,
    isUnpromoting: unpromoteMutation.isPending,
    isDeleting: deleteMutation.isPending,

    // Error states
    promoteError: promoteMutation.error,
    updateError: updateMutation.error,
    unpromoteError: unpromoteMutation.error,
    deleteError: deleteMutation.error,

    // Queries
    promotedEvents: promotedEventsQuery.data?.promoted_events || [],
    promotedEventsLoading: promotedEventsQuery.isLoading,
    promotedEventsError: promotedEventsQuery.error,
    refetchPromotedEvents: promotedEventsQuery.refetch,

    // Helper functions
    getPromotionStatusQueryOptions,
  };
}

export function usePromotionStatus(eventId: string) {
  const { adminAPIClient } = useApi();
  
  return useQuery({
    queryKey: ["admin", "promotion-status", eventId],
    queryFn: () => adminAPIClient.getPromotionStatus(eventId),
    enabled: !!eventId,
  });
}

