import { useForm } from "react-hook-form";
import { useEventPromotion } from "../hooks/useEventPromotion";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Textarea } from "@/shared/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import type { PromotionType, EventPromotion } from "../types/promotion";

interface PromotionFormData {
  priority: number;
  expiresAt: string;
  promotedBy: string;
  promotionType: PromotionType;
  notes: string;
}

interface PromoteEventFormProps {
  eventId: string;
  eventName: string;
  isPromoted?: boolean;
  currentPromotion?: EventPromotion | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

/**
 * Form for promoting/unpromoting events
 * Supports separate EventPromotion table (Option 2)
 */
export function PromoteEventForm({
  eventId,
  eventName,
  isPromoted = false,
  currentPromotion = null,
  onSuccess,
  onCancel,
}: PromoteEventFormProps) {
  const {
    promoteEvent,
    updatePromotion,
    unpromoteEvent,
    deletePromotion,
    isPromoting,
    isUpdating,
    isUnpromoting,
    isDeleting,
    promoteError,
    updateError,
    unpromoteError,
    deleteError,
  } = useEventPromotion();

  const form = useForm<PromotionFormData>({
    defaultValues: {
      priority: currentPromotion?.priority ?? 1,
      expiresAt: currentPromotion?.expires_at ? new Date(currentPromotion.expires_at).toISOString().slice(0, 16) : "",
      promotedBy: currentPromotion?.promoted_by ?? "",
      promotionType: currentPromotion?.promotion_type ?? "standard",
      notes: currentPromotion?.notes ?? "",
    },
  });

  const onSubmit = async (data: PromotionFormData) => {
    try {
      // Format data for API
      const requestData = {
        priority: data.priority,
        expires_at: data.expiresAt ? new Date(data.expiresAt).toISOString() : undefined,
        promoted_by: data.promotedBy || undefined,
        promotion_type: data.promotionType,
        notes: data.notes,
      };

      // Always try to promote first - if it fails with "already promoted", then update
      try {
        await promoteEvent(eventId, requestData);
        alert("Event promoted successfully!");
        onSuccess?.();
      } catch (promoteError: unknown) {
        // Check if the error is because event is already promoted
        const error = promoteError as { response?: { data?: { error?: string } }; message?: string };
        const errorMessage = error?.response?.data?.error || error?.message || "";
        if (errorMessage.includes("already promoted") || errorMessage.includes("Use PATCH to update")) {
          // Event is already promoted, so update instead
          await updatePromotion(eventId, requestData);
          alert("Promotion updated successfully!");
          onSuccess?.();
        } else {
          // Re-throw other errors
          throw promoteError;
        }
      }
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  const handleUnpromote = async () => {
    if (!confirm("Are you sure you want to unpromote this event?")) {
      return;
    }

    try {
      await unpromoteEvent(eventId);
      alert("Event unpromoted successfully!");
      onSuccess?.();
    } catch (error) {
      console.error("Error unpromoting event:", error);
    }
  };

  const handleDelete = async () => {
    if (
      !confirm(
        "Are you sure you want to PERMANENTLY DELETE this promotion? This cannot be undone."
      )
    ) {
      return;
    }

    try {
      await deletePromotion(eventId);
      alert("Promotion deleted successfully!");
      onSuccess?.();
    } catch (error) {
      console.error("Error deleting promotion:", error);
    }
  };

  const isLoading = isPromoting || isUpdating || isUnpromoting || isDeleting || form.formState.isSubmitting;
  const currentError = promoteError || updateError || unpromoteError || deleteError;

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold ">
          Promote Event
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        {currentError && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Error
                </h3>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  {currentError.message}
                </div>
              </div>
            </div>
          </div>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Event Info (Read-only) */}
          <div className="space-y-2">
            <label htmlFor="event-name" className="block text-sm font-medium ">
              Event Name
            </label>
            <Input
              id="event-name"
              type="text"
              value={eventName}
              disabled
              className="bg-gray-50 dark:bg-gray-700  cursor-not-allowed"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="event-id" className="block text-sm font-medium ">
              Event ID
            </label>
            <Input
              id="event-id"
              type="text"
              value={eventId}
              disabled
              className="bg-gray-50 dark:bg-gray-700  cursor-not-allowed"
            />
          </div>

            {/* Priority */}
            <FormField
              control={form.control}
              name="priority"
              rules={{ 
                required: "Priority is required",
                min: { value: 1, message: "Priority must be at least 1" },
                max: { value: 10, message: "Priority must be at most 10" }
              }}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Priority (1-10)
                    <span className="block text-xs  font-normal">
                      Lower values are more prominent
                    </span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="1"
                      max="10"
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Promotion Type */}
            <FormField
              control={form.control}
              name="promotionType"
              rules={{ required: "Promotion type is required" }}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Promotion Type</FormLabel>
                  <FormControl>
                    <select
                      disabled={isLoading}
                      className="flex h-9 w-full rounded-md border border-gray-300 bg-white px-3 py-1 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 md:text-sm"
                      {...field}
                    >
                      <option value="standard">Standard</option>
                      <option value="featured">Featured</option>
                      <option value="urgent">Urgent</option>
                      <option value="sponsored">Sponsored</option>
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Expiration Date */}
            <FormField
              control={form.control}
              name="expiresAt"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Expires At (Optional)
                    <span className="block text-xs  font-normal">
                      Leave blank for no expiration
                    </span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="datetime-local"
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Promoted By (only for new promotions) */}
            {!isPromoted && (
              <FormField
                control={form.control}
                name="promotedBy"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Promoted By (Optional)
                      <span className="block text-xs  font-normal">
                        Username or email (defaults to you)
                      </span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="text"
                        placeholder="admin@example.com"
                        disabled={isLoading}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Internal Notes (Optional)
                    <span className="block text-xs  font-normal">
                      Not visible to users
                    </span>
                  </FormLabel>
                  <FormControl>
                    <Textarea
                      rows={3}
                      placeholder="Why is this event being promoted?"
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

          {/* Actions */}
          <div className="flex flex-wrap gap-3 pt-6">
            {/* Primary Action */}
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              {isPromoting
                ? "Promoting..."
                : isUpdating
                ? "Updating..."
                : "Promote/Update Event"}
            </Button>

            {/* Unpromote (only if promoted) */}
            {isPromoted && (
              <Button
                type="button"
                onClick={handleUnpromote}
                disabled={isLoading}
                variant="outline"
                className="border-amber-500 text-amber-600 hover:bg-amber-50 dark:border-amber-400 dark:text-amber-400 dark:hover:bg-amber-900/20"
              >
                {isUnpromoting ? "Unpromoting..." : "Unpromote"}
              </Button>
            )}

            {/* Delete (only if promoted) */}
            {isPromoted && (
              <Button
                type="button"
                onClick={handleDelete}
                disabled={isLoading}
                variant="destructive"
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </Button>
            )}

            {/* Cancel */}
            {onCancel && (
              <Button
                type="button"
                onClick={onCancel}
                disabled={isLoading}
                variant="outline"
              >
                Cancel
              </Button>
            )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

export default PromoteEventForm;

