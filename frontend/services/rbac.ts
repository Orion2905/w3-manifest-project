import { apiClient } from './api';
import { Role, Permission, UserPermission } from '@/types/auth';

interface RolesResponse {
  roles: Role[];
}

interface PermissionsResponse {
  permissions: Record<string, Permission[]>;
  total: number;
}

interface UserPermissionsResponse {
  user_id: number;
  username: string;
  role: string;
  permissions: string[];
  role_permissions: string[];
  individual_permissions: {
    permission: string;
    granted: boolean;
    granted_at?: string;
    granted_by?: string;
  }[];
}

interface RolePermissionsResponse {
  role_id: number;
  role_name: string;
  role_display: string;
  permissions: Permission[];
}

interface AssignRoleRequest {
  role: string;
}

interface GrantPermissionRequest {
  permission: string;
  granted: boolean;
}

interface UpdateRolePermissionsRequest {
  permission_ids: number[];
}

interface CheckPermissionRequest {
  permission: string;
  resource?: string;
}

interface CheckPermissionResponse {
  user_id: number;
  permission: string;
  resource?: string;
  has_permission: boolean;
}

export const rbacService = {
  // Get all roles
  async getRoles(): Promise<Role[]> {
    const response = await apiClient.get<RolesResponse>('/rbac/roles');
    return response.roles;
  },

  // Get all permissions grouped by resource
  async getPermissions(): Promise<{ permissions: Record<string, Permission[]>; total: number }> {
    const response = await apiClient.get<PermissionsResponse>('/rbac/permissions');
    return response;
  },

  // Assign role to user
  async assignRole(userId: number, role: string): Promise<void> {
    const data: AssignRoleRequest = { role };
    await apiClient.put(`/rbac/user/${userId}/role`, data);
  },

  // Get user permissions
  async getUserPermissions(userId: number): Promise<UserPermissionsResponse> {
    const response = await apiClient.get<UserPermissionsResponse>(`/rbac/user/${userId}/permissions`);
    return response;
  },

  // Grant or revoke permission for user
  async grantUserPermission(userId: number, permission: string, granted: boolean = true): Promise<void> {
    const data: GrantPermissionRequest = { permission, granted };
    await apiClient.post(`/rbac/user/${userId}/permissions`, data);
  },

  // Get role permissions
  async getRolePermissions(roleId: number): Promise<RolePermissionsResponse> {
    const response = await apiClient.get<RolePermissionsResponse>(`/rbac/role/${roleId}/permissions`);
    return response;
  },

  // Update role permissions
  async updateRolePermissions(roleId: number, permissionIds: number[]): Promise<void> {
    const data: UpdateRolePermissionsRequest = { permission_ids: permissionIds };
    await apiClient.put(`/rbac/role/${roleId}/permissions`, data);
  },

  // Check if current user has permission
  async checkPermission(permission: string, resource?: string): Promise<boolean> {
    const data: CheckPermissionRequest = { permission, resource };
    const response = await apiClient.post<CheckPermissionResponse>('/rbac/check-permission', data);
    return response.has_permission;
  }
};

export default rbacService;
