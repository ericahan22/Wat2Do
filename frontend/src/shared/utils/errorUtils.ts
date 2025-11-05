/**
 * Utility functions for handling API errors
 */

export interface APIError {
  message: string;
  status?: number;
}

/**
 * Extract error message from API response
 * Handles both Axios errors and direct API responses
 */
export function extractAPIError(error: unknown): APIError | null {
  if (!error) return null;

  // Handle Axios errors (most common case)
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as { response: { data: unknown; status: number; statusText: string } };
    const response = axiosError.response;
    const data = response.data;
    
    // Check if the response has an error field (Django REST framework format)
    if (data && typeof data === 'object' && data !== null && 'error' in data) {
      const errorData = data as { error: string };
      return {
        message: errorData.error,
        status: response.status,
      };
    }
    
    // Fallback to status text or generic message
    const messageData = data as { message?: string; detail?: string } | null;
    return {
      message: messageData?.message || messageData?.detail || response.statusText || 'An error occurred',
      status: response.status,
    };
  }
  
  // Handle network errors
  if (typeof error === 'object' && error !== null && 'request' in error) {
    return {
      message: 'Network error. Please check your connection.',
      status: 0,
    };
  }
  
  // Handle other errors
  if (typeof error === 'object' && error !== null && 'message' in error) {
    const errorWithMessage = error as { message: string };
    return {
      message: errorWithMessage.message,
    };
  }
  
  return {
    message: 'An unexpected error occurred',
  };
}

/**
 * Get a user-friendly error message from an API error
 */
export function getErrorMessage(error: unknown): string {
  const apiError = extractAPIError(error);
  return apiError?.message || 'An error occurred';
}
