import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useUser } from "@clerk/clerk-react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { ArrowLeft, Save, Check, X, Calendar } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Form } from "@/shared/components/ui/form";
import { useApi } from "@/shared/hooks/useApi";
import { Event } from "@/features/events/types/events";
import { utcToLocal, localToUtc } from "@/shared/lib/dateUtils";
import { EventFormFields, EventFormData } from "./EventFormFields";

interface EventEditFormProps {
  event: Event;
}

export function EventEditForm({ event }: EventEditFormProps) {
  const navigate = useNavigate();
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === "admin";
  const queryClient = useQueryClient();
  const { eventsAPIClient } = useApi();

  const form = useForm<EventFormData>({
    defaultValues: {
      title: event.title || "",
      description: event.description || "",
      location: event.location || "",
      occurrences:
        event.occurrences && event.occurrences.length > 0
          ? event.occurrences.map((d) => ({
              dtstart_local: utcToLocal(d.dtstart_utc),
              dtend_local: d.dtend_utc ? utcToLocal(d.dtend_utc) : "",
            }))
          : [{ dtstart_local: "", dtend_local: "" }],
      price: event.price ?? null,
      food: event.food || "",
      registration: event.registration || false,
      source_url: event.source_url || "",
    },
  });

  const updateEventMutation = useMutation({
    mutationFn: (eventData: EventFormData) =>
      eventsAPIClient.updateEvent(Number(event.id), eventData as unknown as Record<string, unknown>),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["event", event.id] });
      toast.success("Event updated successfully");
    },
  });

  const reviewSubmissionMutation = useMutation({
    mutationFn: async ({ action }: { action: "approve" | "reject" }) => {
      if (!event?.id) {
        throw new Error("No submission found");
      }
      return eventsAPIClient.reviewSubmission(event.id, action);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["event", event.id] });
      if (variables.action === "approve") {
        toast.success("Event approved successfully");
      } else {
        toast.success("Event rejected");
      }
    },
  });

  const handleBack = () => {
    navigate(-1);
  };

  const onSubmit = (data: EventFormData) => {
    const submitData = {
      ...data,
      occurrences: data.occurrences.map((d) => ({
        dtstart_utc: localToUtc(d.dtstart_local),
        dtend_utc: d.dtend_local ? localToUtc(d.dtend_local) : null,
      })),
    };
    updateEventMutation.mutate(submitData as unknown as EventFormData);
  };

  const handleApprove = () => {
    reviewSubmissionMutation.mutate({ action: "approve" });
  };

  const handleReject = () => {
    reviewSubmissionMutation.mutate({ action: "reject" });
  };

  return (
    <div className="max-w-xl mx-auto">
      {/* Back Button */}
      <div className="mb-6">
        <Button onMouseDown={handleBack} variant="ghost" className="p-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Events
        </Button>
      </div>

      {/* Edit Mode */}
      <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Edit Event Data
          </h2>
          <div className="flex gap-2">
            {isAdmin && event.id && event.status === "PENDING" && (
              <>
                <Button
                  onClick={handleApprove}
                  disabled={reviewSubmissionMutation.isPending}
                  variant="default"
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Check className="h-4 w-4 mr-2" />
                  Approve
                </Button>
                <Button
                  onClick={handleReject}
                  disabled={reviewSubmissionMutation.isPending}
                  variant="destructive"
                >
                  <X className="h-4 w-4 mr-2" />
                  Reject
                </Button>
              </>
            )}
            <Button
              onClick={form.handleSubmit(onSubmit)}
              disabled={updateEventMutation.isPending}
              variant="default"
            >
              <Save className="h-4 w-4" />
              {updateEventMutation.isPending ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>

        <div className="relative mb-4">
          {event.source_image_url ? (
            <img
              src={event.source_image_url}
              alt="Event Image"
              className="w-full h-auto rounded-lg"
            />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-700 dark:to-gray-600 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Calendar className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 text-lg">
                  No image available
                </p>
              </div>
            </div>
          )}
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <EventFormFields form={form} isDisabled={updateEventMutation.isPending} />
          </form>
        </Form>
      </div>
    </div>
  );
}
