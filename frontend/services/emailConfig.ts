import { apiClient } from './api';
import { 
  EmailConfig, 
  CreateEmailConfigData, 
  UpdateEmailConfigData,
  EmailLog,
  EmailTestResult,
  MonitoringStatus,
  EmailConfigFilters,
  EmailLogFilters
} from '@/types/emailConfig';
import { PaginatedResponse } from '@/types/api';

export const emailConfigService = {
  // Get all email configurations
  async getEmailConfigs(filters?: EmailConfigFilters): Promise<{
    success: boolean;
    data: EmailConfig[];
    total: number;
  }> {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters.has_errors !== undefined) params.append('has_errors', filters.has_errors.toString());
      if (filters.search) params.append('search', filters.search);
    }

    const queryString = params.toString();
    const url = `/email-config${queryString ? `?${queryString}` : ''}`;
    
    return apiClient.get(url);
  },

  // Get specific email configuration
  async getEmailConfig(id: number): Promise<{
    success: boolean;
    data: EmailConfig;
  }> {
    return apiClient.get(`/email-config/${id}`);
  },

  // Create new email configuration
  async createEmailConfig(data: CreateEmailConfigData): Promise<{
    success: boolean;
    message: string;
    data: EmailConfig;
  }> {
    return apiClient.post('/email-config', data);
  },

  // Update email configuration
  async updateEmailConfig(id: number, data: UpdateEmailConfigData): Promise<{
    success: boolean;
    message: string;
    data: EmailConfig;
  }> {
    return apiClient.put(`/email-config/${id}`, data);
  },

  // Delete email configuration
  async deleteEmailConfig(id: number): Promise<{
    success: boolean;
    message: string;
  }> {
    return apiClient.delete(`/email-config/${id}`);
  },

  // Test email configuration
  async testEmailConfig(id: number): Promise<EmailTestResult> {
    return apiClient.post(`/email-config/${id}/test`);
  },

  // Get email logs for specific configuration
  async getEmailLogs(params: any = {}): Promise<{
    success: boolean;
    data: EmailLog[];
    pagination: {
      page: number;
      pages: number;
      per_page: number;
      total: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    const searchParams = new URLSearchParams();
    
    // Add pagination
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    
    // Add filters
    if (params.config_id) searchParams.append('config_id', params.config_id.toString());
    if (params.level) searchParams.append('level', params.level);
    if (params.search) searchParams.append('search', params.search);
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);

    return apiClient.get(`/email-config/logs?${searchParams.toString()}`);
  },

  // Get email logs for specific configuration (legacy method)
  async getEmailLogsForConfig(
    configId: number,
    page: number = 1,
    limit: number = 50
  ): Promise<{
    success: boolean;
    data: EmailLog[];
    pagination: {
      page: number;
      pages: number;
      per_page: number;
      total: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    return apiClient.get(`/email-config/${configId}/logs?${params.toString()}`);
  },

  // Get all email logs with filters
  async getAllEmailLogs(
    page: number = 1,
    limit: number = 50,
    filters?: EmailLogFilters
  ): Promise<{
    success: boolean;
    data: EmailLog[];
    pagination: {
      page: number;
      pages: number;
      per_page: number;
      total: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    if (filters) {
      if (filters.status) params.append('status', filters.status);
      if (filters.action) params.append('action', filters.action);
      if (filters.config_id) params.append('config_id', filters.config_id.toString());
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
    }

    return apiClient.get(`/email-config/logs?${params.toString()}`);
  },

  // Get monitoring status
  async getMonitoringStatus(): Promise<{
    success: boolean;
    data: MonitoringStatus;
  }> {
    return apiClient.get('/email-config/status');
  },

  // Get realtime logs for monitoring
  async getRealtimeLogs(params: any = {}): Promise<{
    success: boolean;
    data: {
      logs: any[];
      count: number;
      server_time: number;
    };
  }> {
    const searchParams = new URLSearchParams();
    
    if (params.since) searchParams.append('since', params.since.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());

    return apiClient.get(`/email-config/realtime-logs?${searchParams.toString()}`);
  },

  // Simulate email for testing
  async simulateEmail(params: {
    config_id: number;
    subject?: string;
    sender?: string;
    action?: 'processed' | 'ignored' | 'error';
    filter_reason?: string;
    error_message?: string;
  }): Promise<{
    success: boolean;
    data: {
      log_id: number;
      message: string;
    };
  }> {
    return apiClient.post('/email-config/simulate-email', params);
  },

  // Helper methods for data formatting
  formatLastCheck(dateString?: string): string {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minute(s) ago`;
    if (diffHours < 24) return `${diffHours} hour(s) ago`;
    return `${diffDays} day(s) ago`;
  },

  getStatusColor(config: EmailConfig): 'green' | 'yellow' | 'red' | 'gray' {
    if (!config.is_active) return 'gray';
    if (config.last_error) return 'red';
    if (!config.last_success) return 'yellow';
    
    // Check if last success was recent (within 24 hours)
    const lastSuccess = new Date(config.last_success);
    const now = new Date();
    const diffMs = now.getTime() - lastSuccess.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);
    
    if (diffHours > 24) return 'yellow';
    return 'green';
  },

  getStatusText(config: EmailConfig): string {
    if (!config.is_active) return 'Inactive';
    if (config.last_error) return 'Error';
    if (!config.last_success) return 'Not tested';
    
    const lastSuccess = new Date(config.last_success);
    const now = new Date();
    const diffMs = now.getTime() - lastSuccess.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);
    
    if (diffHours > 24) return 'Needs attention';
    return 'Healthy';
  }
};
