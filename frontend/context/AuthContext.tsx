'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { User, AuthResponse } from '@/types/auth';
import { authService } from '@/services/auth';
import { apiClient } from '@/services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: { email: string; password: string; name: string; role?: string }) => Promise<void>;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = apiClient.getAuthToken();
        if (token) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        // Token might be invalid, remove it
        apiClient.removeAuthToken();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response: AuthResponse = await authService.login({ email, password });
      apiClient.setAuthToken(response.access_token);
      
      // Also store refresh token if available
      if (response.refresh_token) {
        Cookies.set('refresh_token', response.refresh_token, { expires: 30 }); // 30 days
      }
      
      setUser(response.user);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      // Even if logout fails on server, clear local state
    } finally {
      setUser(null);
    }
  };

  const register = async (data: { email: string; password: string; name: string; role?: string }) => {
    try {
      const registerData = {
        username: data.email,
        email: data.email,
        password: data.password,
        first_name: data.name.split(' ')[0] || data.name,
        last_name: data.name.split(' ').slice(1).join(' ') || '',
        role: data.role || 'user'
      };
      const response: AuthResponse = await authService.register(registerData);
      apiClient.setAuthToken(response.access_token);
      setUser(response.user);
    } catch (error) {
      throw error;
    }
  };

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const isAuthenticated = !!user;

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    register,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
