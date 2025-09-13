'use client';

import React from 'react';
import { useTheme } from '@/context/ThemeContext';
import { MoonIcon, SunIcon } from '@heroicons/react/24/outline';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  className = '', 
  showLabel = false 
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        inline-flex items-center justify-center
        p-2 rounded-lg
        text-gray-500 dark:text-gray-400
        hover:text-gray-900 dark:hover:text-white
        hover:bg-gray-100 dark:hover:bg-gray-700
        focus:outline-none focus:ring-2 focus:ring-blue-500
        transition-all duration-200
        ${className}
      `}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <MoonIcon className="h-5 w-5" />
      ) : (
        <SunIcon className="h-5 w-5" />
      )}
      
      {showLabel && (
        <span className="ml-2 text-sm font-medium">
          {theme === 'light' ? 'Dark' : 'Light'}
        </span>
      )}
    </button>
  );
};

export default ThemeToggle;
