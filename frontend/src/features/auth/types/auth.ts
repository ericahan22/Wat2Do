export interface User {
  id: number;
  email: string;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse {
  user: User;
  message?: string;
}

export interface AuthError {
  message: string;
  status?: number;
}

export interface AuthFormData {
  email: string;
  password: string;
}

export interface AuthMutationOptions {
  onSuccess?: () => void;
  onError?: (error: AuthError) => void;
}
