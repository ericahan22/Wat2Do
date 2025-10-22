const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api`

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
}

export interface User {
  id: number
  email: string
}

export interface AuthResponse {
  ok: boolean
  user?: User
  message?: string
  error?: string
}

export interface ApiError {
  error: string
  detail?: string
}

// Helper function to handle API responses
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData: ApiError = await response.json()
    throw new Error(errorData.error || errorData.detail || 'An error occurred')
  }
  return response.json()
}

// Auth API functions
export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Important for session cookies
      body: JSON.stringify(credentials),
    })
    return handleApiResponse<AuthResponse>(response)
  },

  async signup(userData: SignupRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/signup/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(userData),
    })
    return handleApiResponse<AuthResponse>(response)
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me/`, {
      method: 'GET',
      credentials: 'include',
    })
    return handleApiResponse<User>(response)
  },

  async logout(): Promise<{ ok: boolean }> {
    const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
    })
    return handleApiResponse<{ ok: boolean }>(response)
  },

  async confirmEmail(token: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/confirm/${token}/`, {
      method: 'GET',
      credentials: 'include',
    })
    return handleApiResponse<AuthResponse>(response)
  },
}
