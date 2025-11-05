/**
 * Clerk Auth Store
 * Zustand store for Clerk authentication state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState, ClerkUser, ClerkSession } from '@/shared/types/auth';

interface ClerkAuthStore extends AuthState {
  setUser: (user: ClerkUser | null) => void;
  setSession: (session: ClerkSession | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  updateAuthState: (user: ClerkUser | null, session: ClerkSession | null) => void;
}

export const useClerkAuthStore = create<ClerkAuthStore>()(
  persist(
    (set) => ({
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: true,
      
      setUser: (user) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },
      
      setSession: (session) => {
        set({ session });
      },
      
      setLoading: (isLoading) => {
        set({ isLoading });
      },
      
      logout: () => {
        set({
          user: null,
          session: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },
      
      updateAuthState: (user, session) => {
        set({
          user,
          session,
          isAuthenticated: !!user && !!session,
          isLoading: false,
        });
      },
    }),
    {
      name: 'clerk-auth-storage',
      partialize: (state) => ({
        user: state.user,
        session: state.session,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
