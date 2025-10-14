/**
 * Simple API configuration
 */

import { API_BASE_URL } from '@/shared/constants/api';

/**
 * Simple fetch wrapper that includes credentials for cookies
 */
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    credentials: 'include', // Include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  return fetch(url, { ...defaultOptions, ...options });
}

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/token/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/',
    STATUS: '/auth/status/',
    RESEND_VERIFICATION: '/auth/resend-verification/',
  },
} as const;
