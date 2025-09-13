'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { usePermissions } from '@/hooks/usePermissions';
import { Card, CardContent } from '@/components/ui/Card';
import { HomeIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading } = useAuth();
  const { hasPermission } = usePermissions();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Check admin permissions - if no access, return error content only
  if (!hasPermission('users.manage_roles')) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card>
          <CardContent className="text-center py-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Access Denied
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              You need admin privileges to access the admin panel.
            </p>
            <Link 
              href="/dashboard"
              className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <HomeIcon className="h-4 w-4 mr-2" />
              Return to Dashboard
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Just return children - no Layout wrapper here
  return <>{children}</>;
}
