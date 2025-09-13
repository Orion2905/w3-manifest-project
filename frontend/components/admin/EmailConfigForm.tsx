'use client';

import React, { useState } from 'react';
import { EmailConfig, CreateEmailConfigData, UpdateEmailConfigData } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface EmailConfigFormProps {
  config?: EmailConfig; // If provided, we're editing
  onSuccess: (config: EmailConfig) => void;
  onCancel: () => void;
}

const EmailConfigForm: React.FC<EmailConfigFormProps> = ({
  config,
  onSuccess,
  onCancel
}) => {
  const isEditing = !!config;
  
  const [formData, setFormData] = useState({
    name: config?.name || '',
    imap_server: config?.imap_server || '',
    imap_port: config?.imap_port || 993,
    email: config?.email || '',
    password: '',
    use_ssl: config?.use_ssl !== undefined ? config.use_ssl : true,
    use_starttls: config?.use_starttls || false,
    folder: config?.folder || 'INBOX',
    subject_filter: config?.subject_filter || '',
    sender_filter: config?.sender_filter || '',
    attachment_filter: config?.attachment_filter || '',
    is_active: config?.is_active !== undefined ? config.is_active : true
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Configuration name is required';
    }

    if (!formData.imap_server.trim()) {
      newErrors.imap_server = 'IMAP server is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }

    if (!isEditing && !formData.password.trim()) {
      newErrors.password = 'Password is required';
    }

    if (formData.imap_port < 1 || formData.imap_port > 65535) {
      newErrors.imap_port = 'Port must be between 1 and 65535';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    setTestResult(null);

    try {
      let result;
      
      if (isEditing && config) {
        const updateData: UpdateEmailConfigData = { ...formData };
        if (!formData.password) {
          delete updateData.password; // Don't update password if not provided
        }
        result = await emailConfigService.updateEmailConfig(config.id, updateData);
      } else {
        const createData: CreateEmailConfigData = formData;
        result = await emailConfigService.createEmailConfig(createData);
      }
      
      onSuccess(result.data);
    } catch (error: any) {
      console.error('Form submission error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'An error occurred';
      setErrors({ submit: errorMessage });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTest = async () => {
    if (!validateForm()) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      // For testing, we need to create a temporary config or use existing one
      let configToTest;
      
      if (isEditing && config) {
        // Update the existing config first if we're editing
        const updateData: UpdateEmailConfigData = { ...formData };
        if (!formData.password) {
          delete updateData.password;
        }
        await emailConfigService.updateEmailConfig(config.id, updateData);
        configToTest = config;
      } else {
        // Create the config first
        const createData: CreateEmailConfigData = formData;
        const result = await emailConfigService.createEmailConfig(createData);
        configToTest = result.data;
      }

      // Test the configuration
      const testResponse = await emailConfigService.testEmailConfig(configToTest.id);
      setTestResult(testResponse);
      
      if (testResponse.success) {
        // If test successful and this was a new config, call onSuccess
        if (!isEditing) {
          onSuccess(configToTest);
          return;
        }
      }
    } catch (error: any) {
      console.error('Test error:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Test failed';
      setTestResult({
        success: false,
        message: errorMessage
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {isEditing ? 'Edit Email Configuration' : 'Add Email Configuration'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Configuration Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={errors.name}
              placeholder="e.g., Gmail Manifest Monitor"
              required
            />

            <div className="flex items-center space-x-2 pt-8">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <label htmlFor="is_active" className="text-sm text-gray-700 dark:text-gray-300">
                Active
              </label>
            </div>
          </div>

          {/* IMAP Server Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              IMAP Server Settings
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <Input
                  label="IMAP Server"
                  value={formData.imap_server}
                  onChange={(e) => handleInputChange('imap_server', e.target.value)}
                  error={errors.imap_server}
                  placeholder="imap.gmail.com"
                  required
                />
              </div>
              
              <Input
                label="Port"
                type="number"
                value={formData.imap_port}
                onChange={(e) => handleInputChange('imap_port', parseInt(e.target.value))}
                error={errors.imap_port}
                min={1}
                max={65535}
                required
              />
            </div>

            <div className="flex space-x-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="use_ssl"
                  checked={formData.use_ssl}
                  onChange={(e) => handleInputChange('use_ssl', e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <label htmlFor="use_ssl" className="text-sm text-gray-700 dark:text-gray-300">
                  Use SSL/TLS
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="use_starttls"
                  checked={formData.use_starttls}
                  onChange={(e) => handleInputChange('use_starttls', e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <label htmlFor="use_starttls" className="text-sm text-gray-700 dark:text-gray-300">
                  Use STARTTLS
                </label>
              </div>
            </div>
          </div>

          {/* Authentication */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Authentication
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Email Address"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                error={errors.email}
                placeholder="your-email@domain.com"
                required
              />
              
              <Input
                label={isEditing ? "Password (leave blank to keep current)" : "Password"}
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                error={errors.password}
                placeholder="Enter password or app password"
                required={!isEditing}
              />
            </div>
          </div>

          {/* Email Filtering */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Email Filtering (Optional)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="IMAP Folder"
                value={formData.folder}
                onChange={(e) => handleInputChange('folder', e.target.value)}
                placeholder="INBOX"
              />
              
              <Input
                label="Subject Filter"
                value={formData.subject_filter}
                onChange={(e) => handleInputChange('subject_filter', e.target.value)}
                placeholder="manifest"
                helperText="Filter emails by subject containing this text"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Sender Filter"
                value={formData.sender_filter}
                onChange={(e) => handleInputChange('sender_filter', e.target.value)}
                placeholder="shipping@company.com"
                helperText="Filter emails from specific sender"
              />
              
              <Input
                label="Attachment Filter"
                value={formData.attachment_filter}
                onChange={(e) => handleInputChange('attachment_filter', e.target.value)}
                placeholder=".xlsx,.csv,.xls"
                helperText="Filter by file extensions (comma separated)"
              />
            </div>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`
              p-4 rounded-lg border
              ${testResult.success 
                ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
                : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
              }
            `}>
              <p className={`text-sm font-medium ${
                testResult.success ? 'text-green-800 dark:text-green-400' : 'text-red-800 dark:text-red-400'
              }`}>
                {testResult.success ? '✓ Test Successful' : '✗ Test Failed'}
              </p>
              <p className={`text-sm mt-1 ${
                testResult.success ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
              }`}>
                {testResult.message}
              </p>
            </div>
          )}

          {/* Form Errors */}
          {errors.submit && (
            <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <p className="text-sm text-red-800 dark:text-red-400">
                {errors.submit}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={isSubmitting || isTesting}
            >
              Cancel
            </Button>
            
            <Button
              type="button"
              onClick={handleTest}
              isLoading={isTesting}
              disabled={isSubmitting}
              className="bg-yellow-600 hover:bg-yellow-700 text-white"
            >
              {isTesting ? 'Testing...' : 'Test & Save'}
            </Button>
            
            <Button
              type="submit"
              isLoading={isSubmitting}
              disabled={isTesting}
            >
              {isSubmitting ? 'Saving...' : (isEditing ? 'Update' : 'Create')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmailConfigForm;
