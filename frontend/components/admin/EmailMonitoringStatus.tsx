'use client';

import React, { useEffect, useState } from 'react';
import { EmailConfig } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import MonitoringTips from './MonitoringTips';
import {
  PlayIcon,
  StopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ArrowPathIcon,
  SignalIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

export interface MonitoringStats {
  totalConfigs: number;
  activeConfigs: number;
  healthyConfigs: number;
  errorConfigs: number;
  lastGlobalCheck: string | null;
  emailsToday: number;
  emailsProcessed: number;
  emailsUnread: number;
  lastEmailTime: string | null;
  averageProcessingTime: number;
}

interface EmailMonitoringStatusProps {
  configs: EmailConfig[];
  onRefresh: () => void;
}

const EmailMonitoringStatus: React.FC<EmailMonitoringStatusProps> = ({
  configs,
  onRefresh
}) => {
  const [stats, setStats] = useState<MonitoringStats>({
    totalConfigs: 0,
    activeConfigs: 0,
    healthyConfigs: 0,
    errorConfigs: 0,
    lastGlobalCheck: null,
    emailsToday: 0,
    emailsProcessed: 0,
    emailsUnread: 0,
    lastEmailTime: null,
    averageProcessingTime: 0
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'warning' | 'error'>('healthy');

  useEffect(() => {
    calculateStats();
  }, [configs]);

  const calculateStats = async () => {
    const totalConfigs = configs.length;
    const activeConfigs = configs.filter(c => c.is_active).length;
    const healthyConfigs = configs.filter(c => {
      const status = emailConfigService.getStatusColor(c);
      return status === 'green';
    }).length;
    const errorConfigs = configs.filter(c => {
      const status = emailConfigService.getStatusColor(c);
      return status === 'red';
    }).length;

    // Get the most recent check time
    const lastChecks = configs
      .filter(c => c.last_check)
      .map(c => new Date(c.last_check!))
      .sort((a, b) => b.getTime() - a.getTime());
    
    const lastGlobalCheck = lastChecks.length > 0 
      ? lastChecks[0].toISOString() 
      : null;

    // Get email stats from monitoring endpoint
    try {
      const monitoringResponse = await emailConfigService.getMonitoringStatus();
      const emailStats = monitoringResponse.data;
      
      setStats({
        totalConfigs,
        activeConfigs,
        healthyConfigs,
        errorConfigs,
        lastGlobalCheck,
        emailsToday: emailStats.emails_today || 0,
        emailsProcessed: emailStats.emails_processed || 0,
        emailsUnread: emailStats.emails_unread || 0,
        lastEmailTime: emailStats.last_email_time || null,
        averageProcessingTime: emailStats.average_processing_time || 0
      });
    } catch (error) {
      // Fallback to basic stats if monitoring endpoint fails
      setStats({
        totalConfigs,
        activeConfigs,
        healthyConfigs,
        errorConfigs,
        lastGlobalCheck,
        emailsToday: 0,
        emailsProcessed: 0,
        emailsUnread: 0,
        lastEmailTime: null,
        averageProcessingTime: 0
      });
    }

    // Determine system status  
    if (errorConfigs > 0) {
      setSystemStatus('error');
    } else if (activeConfigs === 0 || healthyConfigs < activeConfigs / 2) {
      setSystemStatus('warning');
    } else {
      setSystemStatus('healthy');
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getSystemStatusIcon = () => {
    switch (systemStatus) {
      case 'healthy':
        return <CheckCircleIcon className="h-8 w-8 text-green-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />;
      case 'error':
        return <XCircleIcon className="h-8 w-8 text-red-600" />;
    }
  };

  const getSystemStatusText = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'All systems operational';
      case 'warning':
        return 'Some issues detected';
      case 'error':
        return 'Critical errors present';
    }
  };

  const getSystemStatusColor = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* System Overview */}
      <Card className={`border-2 ${getSystemStatusColor()}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {getSystemStatusIcon()}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Email Monitoring System
                </h3>
                <p className={`text-sm ${
                  systemStatus === 'healthy' ? 'text-green-700 dark:text-green-400' :
                  systemStatus === 'warning' ? 'text-yellow-700 dark:text-yellow-400' :
                  'text-red-700 dark:text-red-400'
                }`}>
                  {getSystemStatusText()}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {stats.lastGlobalCheck && (
                <div className="text-right">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Last Check</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {emailConfigService.formatLastCheck(stats.lastGlobalCheck)}
                  </p>
                </div>
              )}
              
              <Button
                variant="secondary"
                onClick={handleRefresh}
                isLoading={isRefreshing}
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <SignalIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Configs
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {stats.totalConfigs}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PlayIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Active Configs
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {stats.activeConfigs}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Healthy
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {stats.healthyConfigs}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Errors
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {stats.errorConfigs}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Individual Config Status */}
      {configs.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Configuration Status
            </h3>
            
            <div className="space-y-3">
              {configs.map((config) => {
                const statusColor = emailConfigService.getStatusColor(config);
                const statusText = emailConfigService.getStatusText(config);
                
                return (
                  <div key={config.id} className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-0">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        statusColor === 'green' ? 'bg-green-400' :
                        statusColor === 'red' ? 'bg-red-400' :
                        statusColor === 'yellow' ? 'bg-yellow-400' :
                        'bg-gray-400'
                      }`} />
                      
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {config.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {config.email}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className={`text-sm font-medium ${
                          statusColor === 'green' ? 'text-green-600' :
                          statusColor === 'red' ? 'text-red-600' :
                          statusColor === 'yellow' ? 'text-yellow-600' :
                          'text-gray-400'
                        }`}>
                          {statusText}
                        </p>
                        {config.last_check && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {emailConfigService.formatLastCheck(config.last_check)}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center space-x-1">
                        {config.is_active ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400">
                            Inactive
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Monitoring Tips */}
      <MonitoringTips stats={stats} />
    </div>
  );
};

export default EmailMonitoringStatus;
