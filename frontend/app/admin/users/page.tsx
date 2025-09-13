'use client';

import React from 'react';
import { usePermissions } from '@/hooks/usePermissions';
import Layout from '@/components/layout/Layout';
import UserManagement from '@/components/admin/UserManagement';
import { Card, CardContent } from '@/components/ui/Card';
import { HomeIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function UsersPage() {
  const { hasPermission } = usePermissions();

  // Check admin permissions for user management
  if (!hasPermission('users.manage_roles')) {
    return (
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card>
            <CardContent className="text-center py-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Access Denied
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                You need admin privileges to manage users.
              </p>
              <Link 
                href="/admin"
                className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <HomeIcon className="h-4 w-4 mr-2" />
                Return to Admin Panel
              </Link>
            </CardContent>
          </Card>
        </div>
    );
  }

  return (
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            <li className="inline-flex items-center">
              <Link 
                href="/admin"
                className="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 dark:text-gray-400 dark:hover:text-white"
              >
                Admin Panel
              </Link>
            </li>
            <li>
              <div className="flex items-center">
                <svg 
                  className="w-3 h-3 text-gray-400 mx-1" 
                  aria-hidden="true" 
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 6 10"
                >
                  <path 
                    stroke="currentColor" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth="2" 
                    d="m1 9 4-4-4-4"
                  />
                </svg>
                <span className="ml-1 text-sm font-medium text-gray-500 md:ml-2 dark:text-gray-400">
                  Gestione Utenti
                </span>
              </div>
            </li>
          </ol>
        </nav>

        {/* User Management Component */}
        <UserManagement />
      </div>
  );
}
