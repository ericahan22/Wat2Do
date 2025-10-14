import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocalStorage } from "react-use";
import { API_BASE_URL } from "@/shared/constants/api";
import type {
  PromoteEventRequest,
  UpdatePromotionRequest,
  PromoteEventResponse,
  UpdatePromotionResponse,
  UnpromoteEventResponse,
  PromotionErrorResponse,
  PromotedEventsResponse,
  PromotionStatusResponse,
} from "@/features/admin/types/promotion";

// Removed getAdminToken function as it's no longer needed with useLocalStorage

const promotionApi = {
  async promoteEvent(eventId: string, data: PromoteEventRequest, token: string): Promise<PromoteEventResponse> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/${eventId}/promote/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Token ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData: PromotionErrorResponse = await response.json();
      throw new Error(errorData.error || "Failed to promote event");
    }

    return response.json();
  },

  async updatePromotion(eventId: string, data: UpdatePromotionRequest, token: string): Promise<UpdatePromotionResponse> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/${eventId}/promote/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Token ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData: PromotionErrorResponse = await response.json();
      throw new Error(errorData.error || "Failed to update promotion");
    }

    return response.json();
  },

  async unpromoteEvent(eventId: string, token: string): Promise<UnpromoteEventResponse> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/${eventId}/unpromote/`, {
      method: "POST",
      headers: {
        "Authorization": `Token ${token}`,
      },
    });

    if (!response.ok) {
      const errorData: PromotionErrorResponse = await response.json();
      throw new Error(errorData.error || "Failed to unpromote event");
    }

    return response.json();
  },

  async deletePromotion(eventId: string, token: string): Promise<void> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/${eventId}/promote/`, {
      method: "DELETE",
      headers: {
        "Authorization": `Token ${token}`,
      },
    });

    if (!response.ok && response.status !== 204) {
      const errorData: PromotionErrorResponse = await response.json();
      throw new Error(errorData.error || "Failed to delete promotion");
    }
  },

  async getPromotedEvents(token: string): Promise<PromotedEventsResponse> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/promoted/`, {
      headers: {
        "Authorization": `Token ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch promoted events");
    }

    return response.json();
  },

  async getPromotionStatus(eventId: string, token: string): Promise<PromotionStatusResponse> {
    if (!token) throw new Error("Admin token not found. Please log in.");

    const response = await fetch(`${API_BASE_URL}/promotions/events/${eventId}/promotion-status/`, {
      headers: {
        "Authorization": `Token ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch promotion status");
    }

    return response.json();
  },
};

/**
 * Hook for managing event promotions using React Query
 * Requires admin authentication token
 * 
 * Supports separate EventPromotion table (Option 2)
 */
export function useEventPromotion() {
  const queryClient = useQueryClient();
  const [adminToken] = useLocalStorage<string>('admin_token');

  // Mutations
  const promoteMutation = useMutation({
    mutationFn: ({ eventId, data }: { eventId: string; data: PromoteEventRequest }) =>
      promotionApi.promoteEvent(eventId, data, adminToken!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["promotion-status"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ eventId, data }: { eventId: string; data: UpdatePromotionRequest }) =>
      promotionApi.updatePromotion(eventId, data, adminToken!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["promotion-status"] });
    },
  });

  const unpromoteMutation = useMutation({
    mutationFn: (eventId: string) => promotionApi.unpromoteEvent(eventId, adminToken!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["promotion-status"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (eventId: string) => promotionApi.deletePromotion(eventId, adminToken!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["promoted-events"] });
      queryClient.invalidateQueries({ queryKey: ["promotion-status"] });
    },
  });

  // Queries
  const promotedEventsQuery = useQuery({
    queryKey: ["promoted-events"],
    queryFn: () => promotionApi.getPromotedEvents(adminToken!),
    enabled: !!adminToken,
  });

  const getPromotionStatusQueryOptions = (eventId: string) => ({
    queryKey: ["promotion-status", eventId],
    queryFn: () => promotionApi.getPromotionStatus(eventId, adminToken!),
    enabled: !!eventId && !!adminToken,
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
  const [adminToken] = useLocalStorage<string>('admin_token');
  
  return useQuery({
    queryKey: ["promotion-status", eventId],
    queryFn: () => promotionApi.getPromotionStatus(eventId, adminToken!),
    enabled: !!eventId && !!adminToken,
  });
}

