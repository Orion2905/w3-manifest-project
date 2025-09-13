'use client';

import React from 'react';
import { usePermission, useAnyRole } from '@/hooks/usePermissions';

/**
 * Higher-order component to protect routes based on permissions
 */
export const withPermission = (permission: string, fallback?: React.ComponentType) => {
  return function ProtectedComponent<T extends object>(Component: React.ComponentType<T>) {
    return function WrappedComponent(props: T) {
      const hasPermission = usePermission(permission);
      
      if (!hasPermission) {
        if (fallback) {
          const Fallback = fallback;
          return <Fallback />;
        }
        return (
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
              <p className="text-gray-600">You don&apos;t have permission to access this resource.</p>
              <p className="text-sm text-gray-500 mt-2">Required permission: {permission}</p>
            </div>
          </div>
        );
      }
      
      return <Component {...props} />;
    };
  };
};

/**
 * Higher-order component to protect routes based on roles
 */
export const withRole = (roles: string | string[], fallback?: React.ComponentType) => {
  return function ProtectedComponent<T extends object>(Component: React.ComponentType<T>) {
    return function WrappedComponent(props: T) {
      const rolesArray = Array.isArray(roles) ? roles : [roles];
      const hasRole = useAnyRole(rolesArray);
      
      if (!hasRole) {
        if (fallback) {
          const Fallback = fallback;
          return <Fallback />;
        }
        return (
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
              <p className="text-gray-600">You don&apos;t have the required role to access this resource.</p>
              <p className="text-sm text-gray-500 mt-2">Required roles: {rolesArray.join(', ')}</p>
            </div>
          </div>
        );
      }
      
      return <Component {...props} />;
    };
  };
};

/**
 * Component to conditionally render content based on permissions
 */
export const PermissionGate: React.FC<{
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ permission, children, fallback = null }) => {
  const hasPermission = usePermission(permission);
  return hasPermission ? <>{children}</> : <>{fallback}</>;
};

/**
 * Component to conditionally render content based on roles
 */
export const RoleGate: React.FC<{
  roles: string | string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ roles, children, fallback = null }) => {
  const rolesArray = Array.isArray(roles) ? roles : [roles];
  const hasRole = useAnyRole(rolesArray);
  return hasRole ? <>{children}</> : <>{fallback}</>;
};
