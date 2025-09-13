'use client';

import React, { useState } from 'react';
import { EmailConfig } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  PencilIcon,
  TrashIcon,
  PlayIcon,
  StopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';

interface EmailConfigListProps {
  configs: EmailConfig[];
  onEdit: (config: EmailConfig) => void;
  onDelete: (configName: string) => void;
  onTest: (result: any, configName: string) => void;
}

const EmailConfigList: React.FC<EmailConfigListProps> = ({
  configs,
  onEdit,
  onDelete,
  onTest
}) => {
  const [testingConfigs, setTestingConfigs] = useState<Set<number>>(new Set());
  const [deletingConfigs, setDeletingConfigs] = useState<Set<number>>(new Set());

  const getStatusColor = (config: EmailConfig) => {
    return emailConfigService.getStatusColor(config);
  };

  const getStatusText = (config: EmailConfig) => {
    return emailConfigService.getStatusText(config);
  };

  const getStatusIcon = (config: EmailConfig) => {
    const color = getStatusColor(config);
    
    switch (color) {
      case 'green':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'red':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'yellow':
        return <ClockIcon className="h-5 w-5 text-yellow-600" />;
      case 'gray':
        return <StopIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const handleTest = async (config: EmailConfig) => {
    setTestingConfigs(prev => new Set([...prev, config.id]));
    
    try {
      const result = await emailConfigService.testEmailConfig(config.id);
      onTest(result, config.name);
    } catch (error: any) {
      const result = {
        success: false,
        message: error.response?.data?.message || error.message || 'Test failed'
      };
      onTest(result, config.name);
    } finally {
      setTestingConfigs(prev => {
        const newSet = new Set(prev);
        newSet.delete(config.id);
        return newSet;
      });
    }
  };

  const handleDelete = async (config: EmailConfig) => {
    if (!confirm(`Are you sure you want to delete the configuration "${config.name}"?`)) {
      return;
    }

    setDeletingConfigs(prev => new Set([...prev, config.id]));
    
    try {
      await emailConfigService.deleteEmailConfig(config.id);
      onDelete(config.name);
    } catch (error: any) {
      console.error('Delete failed:', error);
      // Handle error - could show notification
    } finally {
      setDeletingConfigs(prev => {
        const newSet = new Set(prev);
        newSet.delete(config.id);
        return newSet;
      });
    }
  };

  const handleToggleActive = async (config: EmailConfig) => {
    try {
      await emailConfigService.updateEmailConfig(config.id, {
        is_active: !config.is_active
      });
      // Refresh will be handled by parent component
    } catch (error: any) {
      console.error('Toggle failed:', error);
    }
  };

  if (configs.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <EnvelopeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
            No Email Configurations
          </h3>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Get started by creating your first IMAP email configuration.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {configs.map((config) => (
        <Card key={config.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(config)}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {config.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {config.email} • {config.imap_server}:{config.imap_port}
                    </p>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Status
                    </dt>
                    <dd className={`text-sm font-medium ${
                      getStatusColor(config) === 'green' ? 'text-green-600' :
                      getStatusColor(config) === 'red' ? 'text-red-600' :
                      getStatusColor(config) === 'yellow' ? 'text-yellow-600' :
                      'text-gray-400'
                    }`}>
                      {getStatusText(config)}
                    </dd>
                  </div>

                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Last Check
                    </dt>
                    <dd className="text-sm text-gray-900 dark:text-white">
                      {emailConfigService.formatLastCheck(config.last_check)}
                    </dd>
                  </div>

                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Folder
                    </dt>
                    <dd className="text-sm text-gray-900 dark:text-white">
                      {config.folder}
                    </dd>
                  </div>

                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Active
                    </dt>
                    <dd>
                      <button
                        onClick={() => handleToggleActive(config)}
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          config.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                        }`}
                      >
                        {config.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </dd>
                  </div>
                </div>

                {/* Filters */}
                {(config.subject_filter || config.sender_filter || config.attachment_filter) && (
                  <div className="mt-4">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                      Filters
                    </dt>
                    <div className="flex flex-wrap gap-2">
                      {config.subject_filter && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                          Subject: {config.subject_filter}
                        </span>
                      )}
                      {config.sender_filter && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                          Sender: {config.sender_filter}
                        </span>
                      )}
                      {config.attachment_filter && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400">
                          Files: {config.attachment_filter}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {config.last_error && (
                  <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                    <div className="flex">
                      <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />
                      <div>
                        <h4 className="text-sm font-medium text-red-800 dark:text-red-400">
                          Last Error
                        </h4>
                        <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                          {config.last_error}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 ml-4">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleTest(config)}
                  isLoading={testingConfigs.has(config.id)}
                  disabled={deletingConfigs.has(config.id)}
                  title="Test IMAP connection"
                >
                  <PlayIcon className="h-4 w-4" />
                </Button>

                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => onEdit(config)}
                  disabled={testingConfigs.has(config.id) || deletingConfigs.has(config.id)}
                  title="Edit configuration"
                >
                  <PencilIcon className="h-4 w-4" />
                </Button>

                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleDelete(config)}
                  isLoading={deletingConfigs.has(config.id)}
                  disabled={testingConfigs.has(config.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                  title="Delete configuration"
                >
                  <TrashIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default EmailConfigList;
