'use client';

import { useAuth } from '@/context/AuthContext';
import { useMemo } from 'react';

// Permission constants matching backend
export const PERMISSIONS = {
  // Dashboard
  DASHBOARD_VIEW: 'dashboard.view',
  DASHBOARD_ANALYTICS: 'dashboard.analytics',
  
  // Users
  USERS_CREATE: 'users.create',
  USERS_READ: 'users.read',
  USERS_UPDATE: 'users.update',
  USERS_DELETE: 'users.delete',
  USERS_MANAGE_ROLES: 'users.manage_roles',
  USERS_RESET_PASSWORD: 'users.reset_password',
  
  // Orders
  ORDERS_CREATE: 'orders.create',
  ORDERS_READ: 'orders.read',
  ORDERS_UPDATE: 'orders.update',
  ORDERS_DELETE: 'orders.delete',
  ORDERS_EXPORT: 'orders.export',
  ORDERS_ASSIGN: 'orders.assign',
  
  // Manifests
  MANIFESTS_UPLOAD: 'manifests.upload',
  MANIFESTS_READ: 'manifests.read',
  MANIFESTS_UPDATE: 'manifests.update',
  MANIFESTS_DELETE: 'manifests.delete',
  MANIFESTS_PARSE: 'manifests.parse',
  MANIFESTS_APPROVE: 'manifests.approve',
  MANIFESTS_EXPORT: 'manifests.export',
  
  // System
  SYSTEM_LOGS: 'system.logs',
  SYSTEM_SETTINGS: 'system.settings',
  SYSTEM_BACKUP: 'system.backup',
  SYSTEM_MAINTENANCE: 'system.maintenance',
  
  // Reports
  REPORTS_VIEW: 'reports.view',
  REPORTS_CREATE: 'reports.create',
  REPORTS_EXPORT: 'reports.export',
  REPORTS_SCHEDULE: 'reports.schedule',
  
  // API
  API_ACCESS: 'api.access',
  API_ADMIN: 'api.admin'
} as const;

// Role constants
export const ROLES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  OPERATOR: 'operator',
  VIEWER: 'viewer'
} as const;

/**
 * Hook to check if user has a specific permission
 */
export const usePermission = (permission: string) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    if (!user || !user.permissions) return false;
    return user.permissions.includes(permission);
  }, [user, permission]);
};

/**
 * Hook to check multiple permissions (returns object with permission states)
 */
export const usePermissions = (permissions?: string[]) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    const hasPermission = (permission: string): boolean => {
      if (!user || !user.permissions) return false;
      return user.permissions.includes(permission);
    };

    if (!permissions) {
      // Return object with hasPermission function if no specific permissions provided
      return { hasPermission };
    }

    // Return object with permission states if specific permissions provided
    if (!user || !user.permissions) {
      return permissions.reduce((acc, perm) => ({ ...acc, [perm]: false }), { hasPermission });
    }
    
    return permissions.reduce((acc, perm) => ({
      ...acc,
      [perm]: user.permissions!.includes(perm)
    }), { hasPermission } as Record<string, boolean> & { hasPermission: (perm: string) => boolean });
  }, [user, permissions]);
};

/**
 * Hook to check if user has a specific role
 */
export const useRole = (role: string) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    if (!user) return false;
    return user.role_name === role || user.role === role; // Support both new and legacy role fields
  }, [user, role]);
};

/**
 * Hook to check if user has any of the specified roles
 */
export const useAnyRole = (roles: string[]) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    if (!user) return false;
    return roles.some(role => user.role_name === role || user.role === role);
  }, [user, roles]);
};

/**
 * Hook to check if user is admin
 */
export const useIsAdmin = () => {
  return useRole(ROLES.ADMIN);
};

/**
 * Hook to check if user is manager or above
 */
export const useIsManagerOrAbove = () => {
  return useAnyRole([ROLES.ADMIN, ROLES.MANAGER]);
};

/**
 * Hook to check if user can access a resource (has any permission for that resource)
 */
export const useCanAccessResource = (resource: string) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    if (!user || !user.permissions) return false;
    return user.permissions.some(perm => perm.startsWith(`${resource}.`));
  }, [user, resource]);
};

/**
 * Hook to get all permissions for a specific resource
 */
export const useResourcePermissions = (resource: string) => {
  const { user } = useAuth();
  
  return useMemo(() => {
    if (!user || !user.permissions) return [];
    return user.permissions.filter(perm => perm.startsWith(`${resource}.`));
  }, [user, resource]);
};

/**
 * Utility function to check if a user has higher role level than another
 */
export const hasHigherRoleLevel = (userRole: string, targetRole: string): boolean => {
  const roleHierarchy: Record<string, number> = {
    [ROLES.ADMIN]: 4,
    [ROLES.MANAGER]: 3,
    [ROLES.OPERATOR]: 2,
    [ROLES.VIEWER]: 1
  };
  
  const userLevel = roleHierarchy[userRole] || 0;
  const targetLevel = roleHierarchy[targetRole] || 0;
  
  return userLevel > targetLevel;
};
