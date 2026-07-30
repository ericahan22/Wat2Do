// v2-compatible API client. Access tokens stay in memory; refresh lives in
// the backend's httpOnly cookie.
let accessToken: string | null = null;
let refreshPromise: Promise<boolean> | null = null;

const AUTH_CREDENTIAL_ENDPOINTS = new Set([
  "auth/verify-otp",
  "auth/refresh",
  "auth/logout",
]);

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string): void {
  accessToken = token;
}

export function clearAccessToken(): void {
  accessToken = null;
}

function normalizeBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim();
  const baseUrl = configured || (import.meta.env.DEV ? "http://localhost:8000" : "/api");
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, "");

  if (
    import.meta.env.DEV &&
    /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?\/api$/i.test(normalizedBaseUrl)
  ) {
    return normalizedBaseUrl.replace(/\/api$/i, "");
  }

  return normalizedBaseUrl;
}

function normalizeEndpoint(endpoint: string): string {
  return endpoint.replace(/^\/+/, "");
}

function shouldSendCredentials(endpoint: string): boolean {
  return AUTH_CREDENTIAL_ENDPOINTS.has(normalizeEndpoint(endpoint));
}

class BaseAPIClient {
  private _getAuthToken: () => Promise<string | null>;
  private baseUrl: string;

  constructor(getAuthToken: () => Promise<string | null>) {
    this._getAuthToken = getAuthToken;
    this.baseUrl = normalizeBaseUrl();
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  private async refreshAccessToken(): Promise<boolean> {
    if (refreshPromise) return refreshPromise;

    refreshPromise = (async () => {
      try {
        const response = await fetch(`${this.baseUrl}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
        });

        if (!response.ok) return false;
        const data = await response.json() as { access_token?: string };
        if (!data.access_token) return false;
        setAccessToken(data.access_token);
        return true;
      } catch (error) {
        console.error("Token refresh failed:", error);
        return false;
      }
    })().finally(() => {
      refreshPromise = null;
    });

    return refreshPromise;
  }

  async request<T = unknown>({
    endpoint,
    method = "GET",
    body = null,
    retryCount = 0,
  }: {
    endpoint: string;
    method?: string;
    body?: unknown;
    retryCount?: number;
  }): Promise<T> {
    const normalizedEndpoint = normalizeEndpoint(endpoint);
    const token = await this._getAuthToken();
    const headers: HeadersInit = { "Content-Type": "application/json" };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const config: RequestInit = { method, headers };
    if (shouldSendCredentials(normalizedEndpoint)) {
      config.credentials = "include";
    }
    if (body !== null && body !== undefined) {
      config.body = JSON.stringify(body);
    }

    const response = await fetch(`${this.baseUrl}/${normalizedEndpoint}`, config);
    if (response.status === 204) return undefined as T;

    const responseBody = await response.json().catch(() => null);

    if (!response.ok) {
      if (
        response.status === 401 &&
        !normalizedEndpoint.startsWith("auth/") &&
        retryCount === 0
      ) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          return this.request<T>({ endpoint, method, body, retryCount: 1 });
        }
      }

      const message =
        responseBody?.detail ||
        responseBody?.message ||
        responseBody?.error ||
        `HTTP error! status: ${response.status}`;
      const error = new Error(message);
      (error as Error & { data?: unknown; status?: number }).data = responseBody;
      (error as Error & { data?: unknown; status?: number }).status = response.status;
      throw error;
    }

    return responseBody as T;
  }

  getAuthToken(): Promise<string | null> {
    return this._getAuthToken();
  }

  get<T = unknown>(endpoint: string): Promise<T> {
    return this.request<T>({ endpoint, method: "GET" });
  }

  post<T = unknown>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>({ endpoint, method: "POST", body });
  }

  put<T = unknown>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>({ endpoint, method: "PUT", body });
  }

  delete<T = unknown>(endpoint: string): Promise<T> {
    return this.request<T>({ endpoint, method: "DELETE" });
  }
}

export default BaseAPIClient;
