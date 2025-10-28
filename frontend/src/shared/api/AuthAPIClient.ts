import { BaseAPIClient } from './BaseAPIClient';
import type { User, LoginRequest, SignupRequest, AuthResponse } from '@/features/auth/types/auth';

export class AuthAPIClient extends BaseAPIClient {
  constructor() {
    super();
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const headers = await this.getAuthHeaders();
    return this.post<AuthResponse>('/api/auth/login/', credentials, {
      headers
    });
  }

  async signup(userData: SignupRequest): Promise<AuthResponse> {
    const headers = await this.getAuthHeaders();
    return this.post<AuthResponse>('/api/auth/signup/', userData, {
      headers
    });
  }

  async getCurrentUser(): Promise<User> {
    const headers = await this.getAuthHeaders();
    return this.get<User>('/api/auth/me/', {
      headers
    });
  }

  async logout(): Promise<{ ok: boolean }> {
    const headers = await this.getAuthHeaders();
    return this.post<{ ok: boolean }>('/api/auth/logout/', undefined, {
      headers
    });
  }

  async confirmEmail(token: string): Promise<AuthResponse> {
    const headers = await this.getAuthHeaders();
    return this.get<AuthResponse>(`/api/auth/confirm/${token}/`, {
      headers
    });
  }
}

// Export a default instance
export const authAPIClient = new AuthAPIClient();
