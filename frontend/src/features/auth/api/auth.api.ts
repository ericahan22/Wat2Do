import BaseAPIClient, {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/shared/api/BaseAPIClient";
import { DEFAULT_SCHOOL } from "@/shared/lib/school";

const AUTH_EMAIL_KEY = "wat2do:v1:auth-email";
const AUTH_PROFILE_KEY = "wat2do:v1:auth-profile";

const authClient = new BaseAPIClient(async () => getAccessToken());

export interface AuthUser {
  id: string;
  email: string;
  school: string;
}

interface TokenResponse {
  access_token: string;
  user_id: string;
  school?: string | null;
}

interface UserResponse {
  id: string;
  email: string;
  school?: string | null;
}

function saveProfile(profile: AuthUser): void {
  localStorage.setItem(AUTH_PROFILE_KEY, JSON.stringify(profile));
  localStorage.setItem(AUTH_EMAIL_KEY, profile.email);
}

export function getStoredProfile(): AuthUser | null {
  const raw = localStorage.getItem(AUTH_PROFILE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    localStorage.removeItem(AUTH_PROFILE_KEY);
    return null;
  }
}

export function getStoredEmail(): string | null {
  return localStorage.getItem(AUTH_EMAIL_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken() && getStoredEmail());
}

export function clearAuthData(): void {
  clearAccessToken();
  localStorage.removeItem(AUTH_EMAIL_KEY);
  localStorage.removeItem(AUTH_PROFILE_KEY);
}

function toAuthUser(user: UserResponse, fallbackEmail?: string): AuthUser {
  return {
    id: user.id,
    email: user.email || fallbackEmail || "",
    school: user.school?.trim() || DEFAULT_SCHOOL,
  };
}

export async function fetchProfileAPI(fallbackEmail?: string): Promise<AuthUser> {
  const user = await authClient.get<UserResponse>("users/me");
  const profile = toAuthUser(user, fallbackEmail);
  saveProfile(profile);
  return profile;
}

export async function sendOtpAPI(email: string): Promise<void> {
  await authClient.post("auth/send-otp", { email });
}

export async function verifyOtpAPI(email: string, otp: string): Promise<AuthUser> {
  const token = await authClient.post<TokenResponse>("auth/verify-otp", {
    email,
    token: otp,
  });
  setAccessToken(token.access_token);
  localStorage.setItem(AUTH_EMAIL_KEY, email);
  return fetchProfileAPI(email);
}

export async function logoutAPI(): Promise<void> {
  try {
    await authClient.post("auth/logout");
  } catch (error) {
    console.error("Logout request failed; clearing local auth state:", error);
  }
  clearAuthData();
}

export async function initializeAuth(): Promise<AuthUser | null> {
  const email = getStoredEmail();
  if (!email) return null;

  try {
    const token = await authClient.post<TokenResponse>("auth/refresh");
    if (!token.access_token) throw new Error("Refresh did not return an access token.");
    setAccessToken(token.access_token);
    return fetchProfileAPI(email);
  } catch {
    clearAuthData();
    return null;
  }
}
