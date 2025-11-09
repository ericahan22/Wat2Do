// src/api/baseApiClient.js

class BaseAPIClient {
  private _getAuthToken: () => Promise<string | null>;
  private baseUrl: string;

  constructor(getAuthToken: () => Promise<string | null>) {
    this._getAuthToken = getAuthToken;
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
  }

  async request({ endpoint, method = 'GET', body = null }: {
    endpoint: string;
    method?: string;
    body?: unknown;
  }) {
    const token = await this._getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    // console.log('headers', headers);
    const config: RequestInit = {
      method,
      headers,
    };

    if (body) {
      config.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(`${this.baseUrl}/${endpoint}`, config);

      if (!response.ok) {
        // Handle HTTP errors (e.g., 4xx, 5xx)
        const errorData = await response.json().catch(() => ({})); // Try to parse error, otherwise empty object
        throw new Error(errorData.message || errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      // For DELETE or other methods that might not return a body
      if (response.status === 204) {
        return null;
      }
      
      return response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error; // Re-throw so it can be caught by the hook
    }
  }

  // Public method to get auth token (needed for special cases like FormData)
  getAuthToken(): Promise<string | null> {
    return this._getAuthToken();
  }

  // Convenience methods for each HTTP verb
  get(endpoint: string) {
    return this.request({ endpoint, method: 'GET' });
  }

  post(endpoint: string, body?: unknown) {
    return this.request({ endpoint, method: 'POST', body });
  }

  put(endpoint: string, body?: unknown) {
    return this.request({ endpoint, method: 'PUT', body });
  }

  delete(endpoint: string) {
    return this.request({ endpoint, method: 'DELETE' });
  }
}

export default BaseAPIClient;