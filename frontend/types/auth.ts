export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string; // Legacy field for backward compatibility
  role_name: string; // New RBAC role name
  role_display: string; // Display-friendly role name
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  department?: string;
  phone?: string;
  timezone: string;
  language: string;
  permissions?: string[]; // Array of permission strings
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface Role {
  id: number;
  name: string;
  display_name: string;
  description: string;
  is_active: boolean;
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: number;
  name: string;
  resource: string;
  action: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface UserPermission {
  permission: string;
  granted: boolean;
  granted_at?: string;
  granted_by?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}
