export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  errors?: string[];
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

export type Theme = 'light' | 'dark';

export interface AppSettings {
  theme: Theme;
  language: string;
  notifications: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
}

// Re-export types for convenience
export * from './auth';
export * from './orders';
export * from './manifest';
