import { z } from 'zod';

export const submissionSchema = z.object({
  screenshot: z
    .instanceof(File)
    .refine((file) => file.size <= 10 * 1024 * 1024, 'File must be less than 10MB')
    .refine(
      (file) => ['image/jpeg', 'image/png', 'image/webp'].includes(file.type),
      'File must be JPEG, PNG, or WEBP'
    ),
  source_url: z
    .string()
    .min(1, 'Event URL is required')
    .url('Please enter a valid URL'),
  other_handle: z
    .string()
    .trim()
    .url('Please enter a valid URL')
    .optional()
    .or(z.literal('').transform(() => undefined)),
});

export type SubmissionFormData = z.infer<typeof submissionSchema>;
