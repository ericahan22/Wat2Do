import { create } from "zustand";
import type { AuthUser } from "@/features/auth/api/auth.api";
import {
  getStoredProfile,
  initializeAuth,
  logoutAPI,
  sendOtpAPI,
  verifyOtpAPI,
} from "@/features/auth/api/auth.api";

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  setUser: (user: AuthUser | null) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: getStoredProfile(),
  isLoading: true,
  setUser: (user) => set({ user }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export function useAuthState() {
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);
  return {
    user,
    isLoading,
    isSignedIn: Boolean(user),
  };
}

export async function initializeAuthState(): Promise<void> {
  useAuthStore.getState().setLoading(true);
  const user = await initializeAuth();
  useAuthStore.getState().setUser(user);
  useAuthStore.getState().setLoading(false);
}

export async function sendOtp(email: string): Promise<void> {
  await sendOtpAPI(email);
}

export async function verifyOtp(email: string, otp: string): Promise<void> {
  const user = await verifyOtpAPI(email, otp);
  useAuthStore.getState().setUser(user);
  window.dispatchEvent(new Event("auth-user-login"));
}

export async function logout(): Promise<void> {
  await logoutAPI();
  useAuthStore.getState().setUser(null);
  window.dispatchEvent(new Event("auth-user-logout"));
}
