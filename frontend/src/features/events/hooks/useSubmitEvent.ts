import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/shared/lib/api';
import { SubmittedEvent } from '../types/events';

interface SubmitEventData {
  name: string;
  date: string;
  startTime: string;
  endTime: string;
  location: string;
  description: string;
  price: number | null;
  food: string;
  clubHandle: string;
  clubType: string;
  url: string;
  registration: boolean;
}

export function useSubmitEvent() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({ data, imageFile }: { data: SubmitEventData; imageFile: File }): Promise<SubmittedEvent> => {
      const formData = new FormData();
      
      // Add all form fields
      Object.entries(data).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          formData.append(key, value.toString());
        }
      });
      
      // Add image file
      formData.append('image', imageFile);

      const response = await apiRequest('/events/submit/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit event');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch user submissions
      queryClient.invalidateQueries({ queryKey: ['userSubmissions'] });
    },
  });

  return {
    submitEvent: mutation.mutate,
    isLoading: mutation.isPending,
    error: mutation.error?.message || null,
  };
}
