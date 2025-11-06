import { z } from 'zod';

export const submissionSchema = z.object({
  screenshot_url: z.string().url('Invalid screenshot URL'),
  extracted_data: z.any(), // The JSON object containing event data
});

export type SubmissionFormData = z.infer<typeof submissionSchema>;
