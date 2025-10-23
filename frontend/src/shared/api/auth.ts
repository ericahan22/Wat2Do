import { API_BASE_URL } from '@/shared/constants/api'

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface User {
  id: number
  email: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
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

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getCsrfToken(): string | null {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrftoken') {
      return value
    }
  }
  return null
}

async function fetchCsrfToken(): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/csrf-token/`, {
      method: 'GET',
      credentials: 'include',
    })
    if (response.ok) {
      const data = await response.json()
      return data.csrfToken
    }
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error)
  }
  return null
}

async function getOrFetchCsrfToken(): Promise<string | null> {
  let csrfToken = getCsrfToken()
  if (!csrfToken) {
    csrfToken = await fetchCsrfToken()
  }
  return csrfToken
}

async function createAuthenticatedHeaders(contentType: string = 'application/json'): Promise<Record<string, string>> {
  const csrfToken = await getOrFetchCsrfToken()
  const headers: Record<string, string> = {}
  
  if (contentType) {
    headers['Content-Type'] = contentType
  }
  
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken
  }
  
  return headers
}

async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData: ApiError = await response.json()
    throw new Error(errorData.error || errorData.detail || 'An error occurred')
  }
  return response.json()
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const headers = await createAuthenticatedHeaders()
    
    const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(credentials),
    })
    
    return handleApiResponse<AuthResponse>(response)
  },

  async signup(userData: SignupRequest): Promise<AuthResponse> {
    const headers = await createAuthenticatedHeaders()
    
    const response = await fetch(`${API_BASE_URL}/api/auth/signup/`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(userData),
    })
    
    return handleApiResponse<AuthResponse>(response)
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me/`, {
      method: 'GET',
      credentials: 'include',
    })
    
    return handleApiResponse<User>(response)
  },

  async logout(): Promise<{ ok: boolean }> {
    const headers = await createAuthenticatedHeaders('')
    
    const response = await fetch(`${API_BASE_URL}/api/auth/logout/`, {
      method: 'POST',
      headers,
      credentials: 'include',
    })
    
    return handleApiResponse<{ ok: boolean }>(response)
  },

  async confirmEmail(token: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/confirm/${token}/`, {
      method: 'GET',
      credentials: 'include',
    })
    
    return handleApiResponse<AuthResponse>(response)
  },
}