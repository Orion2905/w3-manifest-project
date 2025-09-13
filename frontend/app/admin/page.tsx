'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { usePermissions } from '@/hooks/usePermissions';
import Layout from '@/components/layout/Layout';
import {
  EnvelopeIcon,
  UsersIcon,
  ChartBarIcon,
  CogIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

export default function AdminPage() {
  const { hasPermission } = usePermissions();

  // Check admin permissions
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
            </CardContent>
          </Card>
        </div>
    );
  }

  const adminSections = [
    {
      title: 'Email Management',
      description: 'Configure and monitor IMAP email connections for manifest processing',
      href: '/admin/email',
      icon: EnvelopeIcon,
      color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
      features: [
        'IMAP Configuration',
        'Email Monitoring',
        'Activity Logs',
        'Connection Testing'
      ]
    },
    {
      title: 'User Management',
      description: 'Manage users, roles, and permissions',
      href: '/admin/users',
      icon: UsersIcon,
      color: 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400',
      features: [
        'User Accounts',
        'Role Assignment',
        'Permission Control',
        'Access Logs'
      ]
    },
    {
      title: 'System Analytics',
      description: 'View system performance and usage statistics',
      href: '/admin/analytics',
      icon: ChartBarIcon,
      color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
      features: [
        'Usage Statistics',
        'Performance Metrics',
        'Error Tracking',
        'Trend Analysis'
      ]
    },
    {
      title: 'Manifest Management',
      description: 'Advanced manifest processing and validation tools',
      href: '/admin/manifests',
      icon: DocumentTextIcon,
      color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400',
      features: [
        'Bulk Processing',
        'Validation Rules',
        'Error Handling',
        'Archive Management'
      ]
    },
    {
      title: 'Security Settings',
      description: 'Configure security policies and access controls',
      href: '/admin/security',
      icon: ShieldCheckIcon,
      color: 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400',
      features: [
        'Access Policies',
        'Authentication',
        'Audit Logs',
        'Security Reports'
      ]
    },
    {
      title: 'System Configuration',
      description: 'Global system settings and configuration',
      href: '/admin/settings',
      icon: CogIcon,
      color: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
      features: [
        'Global Settings',
        'API Configuration',
        'Integration Setup',
        'Backup Settings'
      ]
    }
  ];

  return (
      <div className="space-y-6">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Admin Panel
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage system settings, users, and configurations
          </p>
        </div>

        {/* Quick Actions */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/admin/email"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <EnvelopeIcon className="h-5 w-5 mr-2" />
              Configure Email
            </Link>
            <Link
              href="/admin/users"
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <UsersIcon className="h-5 w-5 mr-2" />
              Manage Users
            </Link>
            <Link
              href="/admin/analytics"
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
            >
              <ChartBarIcon className="h-5 w-5 mr-2" />
              View Analytics
            </Link>
          </div>
        </div>

        {/* Admin Sections Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {adminSections.map((section) => {
            const Icon = section.icon;
            
            return (
              <Link key={section.href} href={section.href}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      <div className={`p-3 rounded-lg ${section.color}`}>
                        <Icon className="h-6 w-6" />
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {section.title}
                    </h3>
                    
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                      {section.description}
                    </p>
                    
                    <div className="space-y-1">
                      {section.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                          {feature}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>

        {/* System Status */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              System Status
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">●</div>
                <p className="text-sm text-gray-600 dark:text-gray-400">API Status</p>
                <p className="text-xs text-green-600">Operational</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">●</div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Database</p>
                <p className="text-xs text-green-600">Connected</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">●</div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Email Service</p>
                <p className="text-xs text-yellow-600">Monitoring</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">●</div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Storage</p>
                <p className="text-xs text-green-600">Available</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
  );
}
