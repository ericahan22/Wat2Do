export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T = unknown> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface ErrorResponse {
  error: string;
  details?: string;
  status: number;
}

export type Theme = "light" | "dark" | "system";

export interface NavbarState {
  isOpen: boolean;
  isScrolled: boolean;
}
