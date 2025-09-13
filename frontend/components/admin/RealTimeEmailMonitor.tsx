'use client';

import React, { useState, useEffect, useRef } from 'react';
import { EmailLog } from '@/types/emailConfig';
import { emailConfigService } from '@/services/emailConfig';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/services/api';

interface RealTimeEmailMonitorProps {
  refreshInterval?: number; // milliseconds
}

interface EmailLogWithDetails extends Omit<EmailLog, 'timestamp'> {
  config_name?: string;
  config_email?: string;
  filter_reason?: string;
  timestamp: number;
}

const RealTimeEmailMonitor: React.FC<RealTimeEmailMonitorProps> = ({ 
  refreshInterval = 5000 
}) => {
  const [logs, setLogs] = useState<EmailLogWithDetails[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<number>(0);
  
  const { isAuthenticated } = useAuth();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // Check if user has valid token
  const hasValidToken = () => {
    const token = apiClient.getAuthToken();
    return token && token.length > 0;
  };

  const fetchRealtimeLogs = async (sinceTimestamp?: number) => {
    try {
      setError(null);
      
      const params: any = {};
      if (sinceTimestamp) {
        params.since = sinceTimestamp.toString();
      } else {
        params.limit = '100';
      }
      
      const response = await emailConfigService.getRealtimeLogs(params);
      
      if (response.success) {
        const newLogs = response.data.logs as EmailLogWithDetails[];
        
        if (sinceTimestamp && newLogs.length > 0) {
          // Add new logs to the top
          setLogs(prevLogs => {
            const combined = [...newLogs, ...prevLogs];
            // Keep only last 200 logs to prevent memory issues
            return combined.slice(0, 200);
          });
          
          // Auto-scroll to top when new logs arrive
          if (logsContainerRef.current) {
            logsContainerRef.current.scrollTop = 0;
          }
        } else {
          // Initial load
          setLogs(newLogs);
        }
        
        setLastUpdate(response.data.server_time);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching realtime logs:', err);
    }
  };

  const startMonitoring = async () => {
    setIsActive(true);
    setLoading(true);
    
    // Initial load
    await fetchRealtimeLogs();
    setLoading(false);
    
    // Set up interval for updates
    intervalRef.current = setInterval(() => {
      fetchRealtimeLogs(lastUpdate);
    }, refreshInterval);
  };

  const stopMonitoring = () => {
    setIsActive(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const simulateEmail = async (type: 'processed' | 'ignored' | 'error') => {
    try {
      // Get first available config for simulation
      const configsResponse = await emailConfigService.getEmailConfigs();
      const configs = configsResponse.data;
      
      if (configs.length === 0) {
        setError('No email configurations available for simulation');
        return;
      }
      
      const config = configs[0];
      
      let simulationData: any = {
        config_id: config.id,
        subject: `Test Email - ${new Date().toLocaleTimeString()}`,
        sender: 'test@example.com',
        action: type
      };
      
      if (type === 'ignored') {
        simulationData.filter_reason = 'Subject does not match filter criteria';
      } else if (type === 'error') {
        simulationData.error_message = 'Failed to download attachment';
      }
      
      const response = await emailConfigService.simulateEmail(simulationData);
      
      if (response.success) {
        // Refresh logs to show the new simulation
        setTimeout(() => fetchRealtimeLogs(lastUpdate), 1000);
      }
    } catch (err) {
      console.error('Error simulating email:', err);
    }
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const getActionIcon = (action: string, status: string) => {
    switch (action) {
      case 'processed':
        return '✅';
      case 'downloaded':
        return '📥';
      case 'ignored':
        return '🚫';
      case 'error':
        return '❌';
      default:
        return '📧';
    }
  };

  const getActionColor = (action: string, status: string) => {
    switch (action) {
      case 'processed':
      case 'downloaded':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'ignored':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString('it-IT');
  };

  // Show authentication required message if not logged in
  if (!isAuthenticated || !hasValidToken()) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="space-y-4">
            <div className="text-6xl">🔐</div>
            <h3 className="text-xl font-semibold text-gray-900">
              Autenticazione Richiesta
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Per utilizzare il monitoraggio email in tempo reale, devi prima effettuare il login 
              come amministratore del sistema.
            </p>
            <div className="pt-4">
              <Button 
                onClick={() => window.location.href = '/login'}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Vai al Login
              </Button>
            </div>
            <div className="text-sm text-gray-500 mt-4">
              <p><strong>Credenziali di test:</strong></p>
              <p>Email: admin@example.com</p>
              <p>Password: admin123</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Control Panel */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Monitoraggio Email in Tempo Reale
              </h3>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
                }`} />
                <span className="text-sm text-gray-600">
                  {isActive ? 'Attivo' : 'Inattivo'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Simulation buttons */}
              {isActive && (
                <div className="flex items-center space-x-1 mr-4">
                  <span className="text-xs text-gray-500 mr-2">Simula:</span>
                  <button
                    onClick={() => simulateEmail('processed')}
                    className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                  >
                    ✅ Accettata
                  </button>
                  <button
                    onClick={() => simulateEmail('ignored')}
                    className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                  >
                    🚫 Rifiutata
                  </button>
                  <button
                    onClick={() => simulateEmail('error')}
                    className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                  >
                    ❌ Errore
                  </button>
                </div>
              )}
              
              {!isActive ? (
                <Button
                  onClick={startMonitoring}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading ? 'Avvio...' : '▶️ Avvia Monitoraggio'}
                </Button>
              ) : (
                <Button
                  onClick={stopMonitoring}
                  className="bg-red-600 hover:bg-red-700"
                >
                  ⏹️ Stop Monitoraggio
                </Button>
              )}
            </div>
          </div>
          
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">⚠️ {error}</p>
            </div>
          )}
          
          {isActive && (
            <div className="mt-3 text-sm text-gray-600">
              📡 Aggiornamento ogni {refreshInterval / 1000} secondi - 
              {logs.length > 0 && (
                <span className="ml-1">
                  Ultimo aggiornamento: {formatTime(lastUpdate)}
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Real-time Logs */}
      <Card>
        <CardContent className="p-0">
          <div className="bg-gray-50 px-4 py-3 border-b">
            <h4 className="font-medium text-gray-900">
              📧 Email in Arrivo ({logs.length})
            </h4>
            <p className="text-sm text-gray-600">
              Monitoraggio in tempo reale delle email e filtri applicati
            </p>
          </div>
          
          <div 
            ref={logsContainerRef}
            className="max-h-96 overflow-y-auto"
          >
            {logs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                {isActive 
                  ? '🔍 In attesa di email...' 
                  : '▶️ Avvia il monitoraggio per vedere le email in tempo reale'
                }
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {logs.map((log, index) => (
                  <div
                    key={`${log.id}-${index}`}
                    className={`p-4 transition-all duration-300 ${
                      index === 0 && lastUpdate > 0 ? 'bg-blue-50 border-l-4 border-blue-400' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <span className="text-2xl flex-shrink-0 mt-1">
                          {getActionIcon(log.action, log.status)}
                        </span>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h5 className="font-medium text-gray-900 truncate">
                              {log.email_subject || 'Nessun oggetto'}
                            </h5>
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${
                              getActionColor(log.action, log.status)
                            }`}>
                              {log.action.toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>
                              <strong>Da:</strong> {log.email_sender || 'Sconosciuto'}
                            </div>
                            <div>
                              <strong>Configurazione:</strong> {log.config_name} ({log.config_email})
                            </div>
                            
                            {log.action === 'ignored' && log.filter_reason && (
                              <div className="text-yellow-700 bg-yellow-50 p-2 rounded border border-yellow-200 mt-2">
                                <strong>🚫 Filtro applicato:</strong> {log.filter_reason}
                              </div>
                            )}
                            
                            {log.action === 'error' && log.message && (
                              <div className="text-red-700 bg-red-50 p-2 rounded border border-red-200 mt-2">
                                <strong>❌ Errore:</strong> {log.message}
                              </div>
                            )}
                            
                            {log.action === 'processed' && (
                              <div className="text-green-700 bg-green-50 p-2 rounded border border-green-200 mt-2">
                                <strong>✅ Email processata con successo</strong>
                                {log.manifest_file && (
                                  <div className="text-sm mt-1">
                                    📎 File: {log.manifest_file}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right text-xs text-gray-500 flex-shrink-0 ml-4">
                        <div>{formatTime(log.timestamp)}</div>
                        <div>{new Date(log.timestamp * 1000).toLocaleDateString('it-IT')}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RealTimeEmailMonitor;
