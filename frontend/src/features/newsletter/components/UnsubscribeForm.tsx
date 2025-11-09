import React from "react";
import { useForm, Controller } from "react-hook-form";
import { Button } from "@/shared/components/ui/button";
import { Label } from "@/shared/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { Textarea } from "@/shared/components/ui/textarea";
import { Loader2 } from "lucide-react";

interface UnsubscribeFormData {
  reason: string;
  feedback?: string;
}

interface UnsubscribeFormProps {
  email: string;
  onSubmit: (reason: string, feedback?: string) => void;
  isSubmitting: boolean;
  error?: Error | null;
}

const UNSUBSCRIBE_REASONS = [
  { value: "Too many emails", label: "Too many emails" },
  { value: "Not relevant to me", label: "Content not relevant to me" },
  { value: "Found events elsewhere", label: "I find events elsewhere" },
  { value: "Graduated/Left UW", label: "Graduated or left UWaterloo" },
  { value: "Technical issues", label: "Technical issues with emails" },
  { value: "Privacy concerns", label: "Privacy concerns" },
  { value: "Other", label: "Other" },
];

const UnsubscribeForm: React.FC<UnsubscribeFormProps> = ({
  email,
  onSubmit,
  isSubmitting,
}) => {
  const {
    control,
    register,
    handleSubmit,
  } = useForm<UnsubscribeFormData>({
    defaultValues: {
      reason: "",
      feedback: "",
    },
  });

  const onFormSubmit = (data: UnsubscribeFormData) => {
    onSubmit(data.reason, data.feedback || undefined);
  };

  return (
    <div className="text-center flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col gap-4">
        <div className="text-4xl">😢</div>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
          We're sorry to see you go!
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          You're about to unsubscribe from the Wat2Do newsletter.
        </p>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <code className="text-sm text-blue-600 dark:text-blue-400">
            {email}
          </code>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          To help us improve, could you let us know why you're unsubscribing?
        </p>
      </div>

      {/* Form section */}
      <form
        onSubmit={handleSubmit(onFormSubmit)}
        className="flex flex-col gap-4"
      >
        <div className="flex flex-col gap-2">
          <Label className="text-left text-sm font-medium">
            Reason for unsubscribing: <span className="text-red-500">*</span>
          </Label>
          <Controller
            name="reason"
            control={control}
            rules={{ required: "Please select a reason for unsubscribing" }}
            render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Please select a reason" />
                </SelectTrigger>
                <SelectContent>
                  {UNSUBSCRIBE_REASONS.map((r) => (
                    <SelectItem key={r.value} value={r.value}>
                      {r.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label className="text-left text-sm font-medium">
            Additional feedback (optional):
          </Label>
          <Textarea
            {...register("feedback")}
            placeholder="Any additional comments or suggestions..."
            rows={3}
          />
        </div>

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Unsubscribing...
            </>
          ) : (
            "Unsubscribe"
          )}
        </Button>
      </form>
    </div>
  );
};

export default UnsubscribeForm;
