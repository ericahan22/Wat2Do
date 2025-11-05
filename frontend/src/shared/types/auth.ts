/**
 * Clerk User Types
 * Type definitions for Clerk user data
 */

export interface ClerkUser {
  id: string;
  emailAddresses: Array<{
    emailAddress: string;
    id: string;
    verification: {
      status: 'verified' | 'unverified';
    };
  }>;
  firstName: string | null;
  lastName: string | null;
  username: string | null;
  imageUrl: string;
  createdAt: number;
  updatedAt: number;
}

export interface ClerkSession {
  id: string;
  userId: string;
  status: 'active' | 'ended';
  expireAt: number;
  lastActiveAt: number;
}

export interface AuthState {
  user: ClerkUser | null;
  session: ClerkSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
