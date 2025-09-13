'use client';

import React, { useState } from 'react';

type TabType = 'configurations' | 'monitoring' | 'realtime' | 'logs';

const SimpleEmailManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('configurations');

  console.log('SimpleEmailManagement rendering, activeTab:', activeTab);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Email Management - Test
        </h1>
        
        {/* Debug Info */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <p className="text-blue-800">
            🔍 <strong>Debug:</strong> Tab attivo: {activeTab}
          </p>
        </div>

        {/* Tabs - Versione Semplice */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('configurations')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'configurations'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                ⚙️ Configurazioni
              </button>
              
              <button
                onClick={() => setActiveTab('monitoring')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'monitoring'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                📊 Monitoraggio
              </button>
              
              <button
                onClick={() => setActiveTab('realtime')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'realtime'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                📡 Tempo Reale
              </button>
              
              <button
                onClick={() => setActiveTab('logs')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'logs'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                📋 Log Attività
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'configurations' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Configurazioni Email</h2>
              <p>Contenuto configurazioni...</p>
            </div>
          )}
          
          {activeTab === 'monitoring' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Monitoraggio Sistema</h2>
              <p>Contenuto monitoraggio...</p>
            </div>
          )}
          
          {activeTab === 'realtime' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">📡 Monitoraggio Tempo Reale</h2>
              <div className="p-4 bg-green-50 border border-green-200 rounded">
                <p className="text-green-800">
                  ✅ <strong>Successo!</strong> Il tab "Tempo Reale" funziona correttamente!
                </p>
                <p className="text-green-700 mt-2">
                  Qui sarà possibile vedere le email in arrivo in tempo reale e verificare l'applicazione dei filtri.
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'logs' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Log delle Attività</h2>
              <p>Contenuto log...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SimpleEmailManagement;
