'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useSidebar } from '@/context/SidebarContext';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { cn } from '@/utils/cn';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, className }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const { isCollapsed } = useSidebar();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If not authenticated, don't show the layout (auth pages will handle their own layout)
  if (!isAuthenticated) {
    return <div className={cn('min-h-screen bg-white dark:bg-gray-900', className)}>{children}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navbar */}
      <Navbar />
      
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <main 
        className={cn(
          'pt-16 min-h-screen transition-all duration-300 ease-in-out',
          isCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <div className={cn('container mx-auto px-4 py-8', className)}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
