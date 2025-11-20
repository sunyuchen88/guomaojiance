import api from './api';

interface LoginRequest {
  username: string;
  password: string;
}

interface User {
  id: number;
  username: string;
  name: string;
  role: string;
  created_at: string;
  last_login_at?: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Login with username and password
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login', credentials);
  return response.data;
}

/**
 * Logout (remove token from client-side)
 */
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    // Ignore errors during logout, just clear local storage
    console.error('Logout error:', error);
  }
}

export default {
  login,
  logout,
};
