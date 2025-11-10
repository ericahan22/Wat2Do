import { z } from 'zod';

export const submissionSchema = z.object({
  source_image_url: z.string().url('Invalid image URL'),
  title: z.string().min(3, 'Title must be at least 3 characters'),
  location: z.string().min(3, 'Location must be at least 3 characters'),
  description: z.string().optional(),
  price: z.number().optional().nullable(),
  food: z.string().optional(),
  registration: z.boolean(),
  occurrences: z.array(z.object({
    dtstart_utc: z.string(),
    dtend_utc: z.string().optional(),
    tz: z.string().optional(),
  })).min(1, 'At least one occurrence is required'),
});

export type SubmissionFormData = z.infer<typeof submissionSchema>;
