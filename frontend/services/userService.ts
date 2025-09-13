import { apiClient } from './api';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  role_name: string;
  role_display: string;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  department?: string;
  phone?: string;
  timezone?: string;
  language?: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
  permissions?: string[];
}

export interface Role {
  id: number;
  name: string;
  display_name: string;
  description: string;
}

export interface CreateUserData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role_id: number;
  is_active?: boolean;
  is_verified?: boolean;
  department?: string;
  phone?: string;
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  role_id?: number;
  is_active?: boolean;
  is_verified?: boolean;
  is_locked?: boolean;
  department?: string;
  phone?: string;
  timezone?: string;
  language?: string;
}

export interface UserFilters {
  search?: string;
  role?: string;
  status?: 'active' | 'inactive' | 'locked' | 'verified' | 'unverified';
  verified?: string;
  page?: number;
  per_page?: number;
  limit?: number;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  locked_users: number;
  verified_users: number;
  unverified_users: number;
  admin_users: number;
  role_distribution: Record<string, { count: number; display_name: string }>;
  recent_users: number;
}

export interface PaginatedUsersResponse {
  users: User[];
  total: number;
  total_pages: number;
  page: number;
  limit: number;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters: {
    search: string;
    role: string;
    status: string;
  };
}

class UserService {
  private baseUrl = '/admin';

  /**
   * Get user statistics
   */
  async getStats(): Promise<UserStats> {
    return apiClient.get<UserStats>(`${this.baseUrl}/users/stats`);
  }

  /**
   * Get user statistics (alias method)
   */
  async getUserStats(): Promise<UserStats> {
    return this.getStats();
  }

  /**
   * Get paginated list of users with optional filters
   */
  async getUsers(filters: UserFilters = {}): Promise<PaginatedUsersResponse> {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.role) params.append('role', filters.role);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.per_page) params.append('per_page', filters.per_page.toString());

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}/users?${queryString}` : `${this.baseUrl}/users`;
    
    return apiClient.get<PaginatedUsersResponse>(url);
  }

  /**
   * Get a specific user by ID
   */
  async getUser(userId: number): Promise<{ user: User }> {
    return apiClient.get<{ user: User }>(`${this.baseUrl}/users/${userId}`);
  }

  /**
   * Create a new user
   */
  async createUser(userData: CreateUserData): Promise<{ message: string; user: User }> {
    return apiClient.post<{ message: string; user: User }>(`${this.baseUrl}/users`, userData);
  }

  /**
   * Update an existing user
   */
  async updateUser(userId: number, userData: UpdateUserData): Promise<{ message: string; user: User }> {
    return apiClient.put<{ message: string; user: User }>(`${this.baseUrl}/users/${userId}`, userData);
  }

  /**
   * Delete a user (soft delete)
   */
  async deleteUser(userId: number): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`${this.baseUrl}/users/${userId}`);
  }

  /**
   * Toggle user active/inactive status
   */
  async toggleUserStatus(userId: number): Promise<{ message: string; user: { id: number; username: string; is_active: boolean } }> {
    return apiClient.patch<{ message: string; user: { id: number; username: string; is_active: boolean } }>(
      `${this.baseUrl}/users/${userId}/toggle-status`
    );
  }

  /**
   * Reset user password
   */
  async resetPassword(userId: number, newPassword: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(`${this.baseUrl}/users/${userId}/reset-password`, {
      new_password: newPassword
    });
  }

  /**
   * Get available roles for user assignment
   */
  async getRoles(): Promise<{ roles: Role[] }> {
    return apiClient.get<{ roles: Role[] }>('/rbac/roles');
  }
}

export const userService = new UserService();
export default userService;
