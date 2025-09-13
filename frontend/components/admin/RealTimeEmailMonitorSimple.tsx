'use client';

import React from 'react';

const RealTimeEmailMonitorSimple: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        📡 Monitoraggio Email in Tempo Reale
      </h3>
      <p className="text-gray-600">
        Componente temporaneo di test - se vedi questo messaggio, il tab funziona!
      </p>
      
      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
        <p className="text-blue-800">
          ✅ Il tab "Tempo Reale" è stato aggiunto correttamente alla dashboard!
        </p>
      </div>
    </div>
  );
};

export default RealTimeEmailMonitorSimple;
