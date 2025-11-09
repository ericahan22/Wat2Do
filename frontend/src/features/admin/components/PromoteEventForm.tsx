import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { useEventPromotion } from "@/features/admin/hooks/useEventPromotion";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Textarea } from "@/shared/components/ui/textarea";
import { Label } from "@/shared/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import type { PromotionType, EventPromotion } from "@/features/admin/types/promotion";

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
      toast.success("Event promoted successfully!");
      onSuccess?.();
    } catch (promoteError: unknown) {
      // Check if the error is because event is already promoted
      const error = promoteError as { response?: { data?: { error?: string } }; message?: string };
      const errorMessage = error?.response?.data?.error || error?.message || "";
      if (errorMessage.includes("already promoted") || errorMessage.includes("Use PATCH to update")) {
        // Event is already promoted, so update instead
        await updatePromotion(eventId, requestData);
        toast.success("Promotion updated successfully!");
        onSuccess?.();
      } else {
        // Re-throw other errors so global handler can catch them
        throw promoteError;
      }
    }
  };

  const handleUnpromote = async () => {
    if (!confirm("Are you sure you want to unpromote this event?")) {
      return;
    }

    await unpromoteEvent(eventId);
    toast.success("Event unpromoted successfully!");
    onSuccess?.();
  };

  const handleDelete = async () => {
    if (
      !confirm(
        "Are you sure you want to PERMANENTLY DELETE this promotion? This cannot be undone."
      )
    ) {
      return;
    }

    await deletePromotion(eventId);
    toast.success("Promotion deleted successfully!");
    onSuccess?.();
  };

  const isLoading = isPromoting || isUpdating || isUnpromoting || isDeleting || form.formState.isSubmitting;

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold ">
          Promote Event
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Event Info (Read-only) */}
          <div className="space-y-2">
            <Label htmlFor="event-name" className="text-sm font-medium">
              Event Name
            </Label>
            <Input
              id="event-name"
              type="text"
              value={eventName}
              disabled
              className="bg-gray-50 dark:bg-gray-700  cursor-not-allowed"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="event-id" className="text-sm font-medium">
              Event ID
            </Label>
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
                    <Select
                      disabled={isLoading}
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select promotion type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard">Standard</SelectItem>
                        <SelectItem value="featured">Featured</SelectItem>
                        <SelectItem value="urgent">Urgent</SelectItem>
                        <SelectItem value="sponsored">Sponsored</SelectItem>
                      </SelectContent>
                    </Select>
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

