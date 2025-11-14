import { useCallback, useState } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Plus, Trash2, Undo2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Checkbox } from "@/shared/components/ui/checkbox";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/shared/components/ui/form";

interface DateField {
  dtstart_local: string;
  dtend_local: string;
}

export interface EventFormData {
  title: string;
  description: string;
  location: string;
  occurrences: DateField[];
  price: number | null;
  food: string;
  registration: boolean;
  source_url: string;
}

interface DeletedDate {
  date: DateField;
  index: number;
  timestamp: number;
}

interface EventFormFieldsProps {
  form: UseFormReturn<EventFormData>;
  isDisabled?: boolean;
  showUndoHistory?: boolean;
}

export function EventFormFields({
  form,
  isDisabled = false,
  showUndoHistory = true,
}: EventFormFieldsProps) {
  const [deletionHistory, setDeletionHistory] = useState<DeletedDate[]>([]);

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "occurrences",
  });

  const handleRemoveDate = useCallback(
    (index: number) => {
      const dateToRemove = form.getValues(`occurrences.${index}`);

      // Add to deletion history
      setDeletionHistory((prev) => [
        ...prev,
        {
          date: dateToRemove,
          index,
          timestamp: Date.now(),
        },
      ]);

      remove(index);
    },
    [form, remove]
  );

  const handleUndo = useCallback(() => {
    if (deletionHistory.length === 0) return;

    const lastDeleted = deletionHistory[deletionHistory.length - 1];
    const currentDates = form.getValues("occurrences");

    // Calculate the correct insertion index
    const deletionsBeforeThis = deletionHistory
      .slice(0, -1)
      .filter((d) => d.index <= lastDeleted.index).length;

    const adjustedIndex = Math.min(
      lastDeleted.index - deletionsBeforeThis,
      currentDates.length
    );

    // Insert the date back at the adjusted position
    const newDates = [
      ...currentDates.slice(0, adjustedIndex),
      lastDeleted.date,
      ...currentDates.slice(adjustedIndex),
    ];

    form.setValue("occurrences", newDates);

    // Remove from deletion history
    setDeletionHistory((prev) => prev.slice(0, -1));
  }, [deletionHistory, form]);

  return (
    <div className="grid grid-cols-1 gap-4">
      {/* Title */}
      <FormField
        control={form.control}
        name="title"
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              Title <span className="text-red-500">*</span>
            </FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder="Event title"
                disabled={isDisabled}
                required
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Description */}
      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Description</FormLabel>
            <FormControl>
              <Textarea
                {...field}
                placeholder="Event description"
                disabled={isDisabled}
                rows={4}
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Location */}
      <FormField
        control={form.control}
        name="location"
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              Location <span className="text-red-500">*</span>
            </FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder="Event location"
                disabled={isDisabled}
                required
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Source URL */}
      <FormField
        control={form.control}
        name="source_url"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Source URL</FormLabel>
            <FormControl>
              <Input
                {...field}
                type="url"
                placeholder="https://example.com/event"
                disabled={isDisabled}
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Dates */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">
            Dates & Times <span className="text-red-500">*</span>
          </Label>
          <div className="flex gap-2">
            {showUndoHistory && deletionHistory.length > 0 && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleUndo}
                disabled={isDisabled}
                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950"
              >
                <Undo2 className="h-4 w-4 mr-1" />
                Undo ({deletionHistory.length})
              </Button>
            )}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ dtstart_local: "", dtend_local: "" })}
              disabled={isDisabled}
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Date
            </Button>
          </div>
        </div>
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="flex gap-4 items-end rounded-lg w-full"
          >
            <FormField
              control={form.control}
              name={`occurrences.${index}.dtstart_local`}
              render={({ field }) => (
                <FormItem className="w-full">
                  <FormLabel>Start Date & Time</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      type="datetime-local"
                      disabled={isDisabled}
                      required
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`occurrences.${index}.dtend_local`}
              render={({ field }) => (
                <FormItem className="w-full">
                  <FormLabel>End Date & Time</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      type="datetime-local"
                      disabled={isDisabled}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            {fields.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                onClick={() => handleRemoveDate(index)}
                disabled={isDisabled}
                className="hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        ))}
      </div>

      {/* Price */}
      <FormField
        control={form.control}
        name="price"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Price</FormLabel>
            <FormControl>
              <Input
                type="number"
                step="0.01"
                min="0"
                {...field}
                value={field.value ?? ""}
                onChange={(e) =>
                  field.onChange(
                    e.target.value ? parseFloat(e.target.value) : null
                  )
                }
                placeholder="0.00"
                disabled={isDisabled}
              />
            </FormControl>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Leave empty for free events
            </p>
          </FormItem>
        )}
      />

      {/* Food */}
      <FormField
        control={form.control}
        name="food"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Food & Drinks</FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder="Free pizza and drinks"
                disabled={isDisabled}
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Registration Checkbox */}
      <FormField
        control={form.control}
        name="registration"
        render={({ field }) => (
          <FormItem className="flex items-center space-x-2">
            <FormControl>
              <Checkbox
                checked={field.value}
                onCheckedChange={field.onChange}
                disabled={isDisabled}
              />
            </FormControl>
            <FormLabel className="cursor-pointer">
              Registration Required
            </FormLabel>
          </FormItem>
        )}
      />

      <p className="text-sm text-gray-500 dark:text-gray-400 pt-2">
        <span className="text-red-500">*</span> Required fields:{" "}
        <strong>title</strong>, <strong>occurrences</strong> (at least one start
        date/time), and <strong>location</strong>.
        <br />
        <span className="text-xs mt-1 block text-gray-400 dark:text-gray-500">
          Note: Times are displayed in your local timezone and will be converted
          to UTC when saved.
        </span>
      </p>
    </div>
  );
}

