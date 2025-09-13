/**
 * Email configuration types for IMAP monitoring
 */

export interface EmailConfig {
  id: number;
  name: string;
  imap_server: string;
  imap_port: number;
  email: string;
  use_ssl: boolean;
  use_starttls: boolean;
  folder: string;
  subject_filter?: string;
  sender_filter?: string;
  attachment_filter?: string;
  is_active: boolean;
  last_check?: string;
  last_success?: string;
  last_error?: string;
  created_at: string;
  updated_at: string;
  created_by: number;
  has_password?: boolean;
}

export interface CreateEmailConfigData {
  name: string;
  imap_server: string;
  imap_port?: number;
  email: string;
  password: string;
  use_ssl?: boolean;
  use_starttls?: boolean;
  folder?: string;
  subject_filter?: string;
  sender_filter?: string;
  attachment_filter?: string;
  is_active?: boolean;
}

export interface UpdateEmailConfigData {
  name?: string;
  imap_server?: string;
  imap_port?: number;
  email?: string;
  password?: string; // Optional - only if changing password
  use_ssl?: boolean;
  use_starttls?: boolean;
  folder?: string;
  subject_filter?: string;
  sender_filter?: string;
  attachment_filter?: string;
  is_active?: boolean;
}

export interface EmailLog {
  id: number;
  config_id: number;
  email_subject?: string;
  email_sender?: string;
  email_date?: string;
  action: 'downloaded' | 'processed' | 'error' | 'ignored';
  manifest_file?: string;
  status: 'success' | 'error' | 'warning';
  message?: string;
  created_at: string;
  config_name?: string; // Included in some responses
  // Additional fields for log viewer
  level: 'INFO' | 'WARNING' | 'ERROR';
  timestamp: string;
  details?: string;
}

export interface EmailTestResult {
  success: boolean;
  message: string;
  data?: {
    server: string;
    port: number;
    email: string;
    folder_info: {
      folder: string;
      message_count: number;
    };
    ssl: boolean;
    starttls: boolean;
  };
  error?: string;
}

export interface MonitoringStatus {
  total_configs: number;
  active_configs: number;
  inactive_configs: number;
  configs_with_errors: number;
  emails_today: number;
  emails_processed: number;
  emails_unread: number;
  last_email_time?: string;
  average_processing_time?: number;
  last_check_times: Array<{
    config_name: string;
    last_check: string;
    last_success?: string;
    has_error: boolean;
    error_message?: string;
  }>;
}

export interface EmailConfigFilters {
  is_active?: boolean;
  has_errors?: boolean;
  search?: string;
}

export interface EmailLogFilters {
  status?: 'success' | 'error' | 'warning';
  action?: 'downloaded' | 'processed' | 'error' | 'ignored';
  config_id?: number;
  date_from?: string;
  date_to?: string;
}
