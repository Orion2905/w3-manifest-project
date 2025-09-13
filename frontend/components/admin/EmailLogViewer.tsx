'use client';

import React, { useState, useEffect } from 'react';
import { EmailLog } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface EmailLogViewerProps {
  configId?: number;
}

interface LogFilters {
  level: 'all' | 'INFO' | 'WARNING' | 'ERROR';
  search: string;
  dateFrom: string;
  dateTo: string;
}

const EmailLogViewer: React.FC<EmailLogViewerProps> = ({ configId }) => {
  const [logs, setLogs] = useState<EmailLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<LogFilters>({
    level: 'all',
    search: '',
    dateFrom: '',
    dateTo: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  const pageSize = 20;

  useEffect(() => {
    loadLogs();
  }, [page, filters, configId]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        limit: pageSize
      };

      // Add filters
      if (configId) params.config_id = configId;
      if (filters.level !== 'all') params.level = filters.level;
      if (filters.search.trim()) params.search = filters.search.trim();
      if (filters.dateFrom) params.date_from = filters.dateFrom;
      if (filters.dateTo) params.date_to = filters.dateTo;

      const response = await emailConfigService.getEmailLogs(params);
      setLogs(response.data);
      setTotalPages(response.pagination.pages);
    } catch (error) {
      console.error('Failed to load logs:', error);
      setLogs([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof LogFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset to first page when filters change
  };

  const resetFilters = () => {
    setFilters({
      level: 'all',
      search: '',
      dateFrom: '',
      dateTo: ''
    });
    setPage(1);
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'ERROR':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'WARNING':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'INFO':
        return <InformationCircleIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'WARNING':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'INFO':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400';
    }
  };

  const formatTimestamp = (log: EmailLog) => {
    // Use timestamp if available, otherwise use created_at
    const dateString = log.timestamp || log.created_at;
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  const getLogLevel = (log: EmailLog) => {
    // If level is available, use it
    if (log.level) return log.level;
    
    // Otherwise, derive from status
    switch (log.status) {
      case 'error':
        return 'ERROR';
      case 'warning':
        return 'WARNING';
      case 'success':
      default:
        return 'INFO';
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Email Activity Logs
              {configId && (
                <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                  (Config ID: {configId})
                </span>
              )}
            </h3>
            
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Level
                </label>
                <select
                  value={filters.level}
                  onChange={(e) => handleFilterChange('level', e.target.value)}
                  className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Levels</option>
                  <option value="INFO">Info</option>
                  <option value="WARNING">Warning</option>
                  <option value="ERROR">Error</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Search
                </label>
                <div className="relative">
                  <Input
                    type="text"
                    placeholder="Search messages..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="pl-10"
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  From Date
                </label>
                <Input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  To Date
                </label>
                <Input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                />
              </div>

              <div className="col-span-full flex justify-end space-x-2">
                <Button variant="secondary" size="sm" onClick={resetFilters}>
                  Reset
                </Button>
                <Button size="sm" onClick={loadLogs}>
                  Apply Filters
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logs List */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading logs...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="p-8 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                No Logs Found
              </h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                No activity logs match your current filters.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {logs.map((log, index) => {
                const { date, time } = formatTimestamp(log);
                const level = getLogLevel(log);
                
                return (
                  <div key={`${log.id}-${index}`} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getLogIcon(level)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLogLevelColor(level)}`}>
                              {level}
                            </span>
                            
                            {log.config_name && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                                {log.config_name}
                              </span>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                            <CalendarIcon className="h-4 w-4" />
                            <span>{date}</span>
                            <ClockIcon className="h-4 w-4" />
                            <span>{time}</span>
                          </div>
                        </div>
                        
                        <p className="mt-2 text-sm text-gray-900 dark:text-white">
                          {log.message || `${log.action} - ${log.status}`}
                        </p>
                        
                        {/* Show email details if available */}
                        {(log.email_subject || log.email_sender) && (
                          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                            {log.email_subject && <p>Subject: {log.email_subject}</p>}
                            {log.email_sender && <p>From: {log.email_sender}</p>}
                            {log.manifest_file && <p>File: {log.manifest_file}</p>}
                          </div>
                        )}
                        
                        {log.details && (
                          <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded-md">
                            <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                              {log.details}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Page {page} of {totalPages}
                {logs.length > 0 && (
                  <span className="ml-2">
                    ({((page - 1) * pageSize) + 1}-{Math.min(page * pageSize, ((page - 1) * pageSize) + logs.length)})
                  </span>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page <= 1 || loading}
                >
                  <ChevronLeftIcon className="h-4 w-4" />
                </Button>
                
                <span className="px-3 py-1 text-sm text-gray-700 dark:text-gray-300">
                  {page}
                </span>
                
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page >= totalPages || loading}
                >
                  <ChevronRightIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EmailLogViewer;
