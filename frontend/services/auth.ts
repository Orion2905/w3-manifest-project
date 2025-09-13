import { apiClient } from './api';
import { AuthResponse, LoginCredentials, RegisterData, User } from '@/types/auth';

export const authService = {
  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Backend expects 'username' field, but we use email as username
    const loginData = {
      username: credentials.email,
      password: credentials.password
    };
    return apiClient.post<AuthResponse>('/auth/login', loginData);
  },

  // Register new user
  async register(data: RegisterData): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/auth/register', data);
  },

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      apiClient.removeAuthToken();
    }
  },

  // Refresh token
  async refreshToken(): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/auth/refresh');
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  },

  // Change password
  async changePassword(data: { current_password: string; new_password: string }): Promise<void> {
    return apiClient.post('/auth/change-password', data);
  },

  // Check if token is valid
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch {
      return false;
    }
  },
};
