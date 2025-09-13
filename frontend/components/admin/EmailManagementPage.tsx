'use client';

import React, { useState, useEffect } from 'react';
import { EmailConfig } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import EmailConfigForm from './EmailConfigForm';
import EmailConfigList from './EmailConfigList';
import EmailMonitoringStatus from './EmailMonitoringStatus';
import MonitoringTips from './MonitoringTips';
import RealTimeEmailMonitor from './RealTimeEmailMonitorSimple';
import EmailLogViewer from './EmailLogViewer';
import {
  PlusIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  DocumentTextIcon,
  InboxIcon
} from '@heroicons/react/24/outline';

type TabType = 'configurations' | 'monitoring' | 'realtime' | 'logs';

const EmailManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('configurations');
  const [configs, setConfigs] = useState<EmailConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConfigForm, setShowConfigForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<EmailConfig | null>(null);

  // Debug: Verifica che il componente si stia renderizzando
  console.log('EmailManagementPage rendering, activeTab:', activeTab);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const response = await emailConfigService.getEmailConfigs();
      setConfigs(response.data);
    } catch (error: any) {
      console.error('Failed to load email configurations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConfig = () => {
    setEditingConfig(null);
    setShowConfigForm(true);
  };

  const handleEditConfig = (config: EmailConfig) => {
    setEditingConfig(config);
    setShowConfigForm(true);
  };

  const handleConfigSaved = (config: EmailConfig) => {
    setShowConfigForm(false);
    setEditingConfig(null);
    loadConfigs();
    console.log(`Email configuration "${config.name}" ${editingConfig ? 'updated' : 'created'} successfully`);
  };

  const handleConfigDeleted = (configName: string) => {
    loadConfigs();
    console.log(`Email configuration "${configName}" deleted successfully`);
  };

  const handleTestResult = (result: any, configName: string) => {
    console.log(`${configName}: ${result.message}`);
  };

  const getTabIcon = (tab: TabType) => {
    switch (tab) {
      case 'configurations':
        return <Cog6ToothIcon className="h-5 w-5" />;
      case 'monitoring':
        return <ChartBarIcon className="h-5 w-5" />;
      case 'realtime':
        return <InboxIcon className="h-5 w-5" />;
      case 'logs':
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  const getTabLabel = (tab: TabType) => {
    switch (tab) {
      case 'configurations':
        return 'Configurazioni';
      case 'monitoring':
        return 'Monitoraggio';
      case 'realtime':
        return 'Tempo Reale';
      case 'logs':
        return 'Log Attività';
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'configurations':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Email Configurations
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Manage IMAP email configurations for manifest monitoring
                </p>
              </div>
              <Button onClick={handleCreateConfig}>
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Configuration
              </Button>
            </div>

            <EmailConfigList
              configs={configs}
              onEdit={handleEditConfig}
              onDelete={handleConfigDeleted}
              onTest={handleTestResult}
            />
          </div>
        );

      case 'monitoring':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Monitoring Status
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Real-time status of email monitoring systems
              </p>
            </div>

            <EmailMonitoringStatus
              configs={configs}
              onRefresh={loadConfigs}
            />
          </div>
        );

      case 'realtime':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                📡 Monitoraggio Email in Tempo Reale
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Visualizza le email in arrivo e verifica l'applicazione dei filtri in tempo reale
              </p>
            </div>

            <RealTimeEmailMonitor />
          </div>
        );

      case 'logs':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Activity Logs
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                View email processing activity and system logs
              </p>
            </div>

            <EmailLogViewer />
          </div>
        );

      default:
        return null;
    }
  };

  const activeConfigs = configs.filter(c => c.is_active).length;
  const healthyConfigs = configs.filter(c => {
    const status = emailConfigService.getStatusColor(c);
    return status === 'green';
  }).length;
  const errorConfigs = configs.filter(c => {
    const status = emailConfigService.getStatusColor(c);
    return status === 'red';
  }).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <InboxIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Email Management
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Configure and monitor IMAP email connections for manifest processing
              </p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Cog6ToothIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Total Configs</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {configs.length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Active</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {activeConfigs}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-6 w-6 bg-green-100 rounded-full flex items-center justify-center">
                    <div className="h-3 w-3 bg-green-600 rounded-full"></div>
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Healthy</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {healthyConfigs}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-6 w-6 bg-red-100 rounded-full flex items-center justify-center">
                    <div className="h-3 w-3 bg-red-600 rounded-full"></div>
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Errors</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {errorConfigs}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {(['configurations', 'monitoring', 'realtime', 'logs'] as TabType[]).map((tab) => {
                console.log('Rendering tab:', tab);
                return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  } flex items-center space-x-2 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  {getTabIcon(tab)}
                  <span>{getTabLabel(tab)}</span>
                </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          renderTabContent()
        )}

        {/* Configuration Form Modal */}
        {showConfigForm && (
          <EmailConfigForm
            config={editingConfig}
            onSuccess={handleConfigSaved}
            onCancel={() => {
              setShowConfigForm(false);
              setEditingConfig(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default EmailManagementPage;
