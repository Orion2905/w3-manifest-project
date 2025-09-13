import React from 'react';

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

interface MonitoringTipsProps {
  stats: MonitoringStats;
}

export default function MonitoringTips({ stats }: MonitoringTipsProps) {
  const generateTips = () => {
    const tips = [];
    
    // Check for no active configurations
    if (stats.activeConfigs === 0) {
      tips.push({
        type: 'error',
        icon: '⚠️',
        title: 'Nessuna Configurazione Attiva',
        message: 'Attiva almeno una configurazione email per iniziare il monitoraggio.',
        action: 'Vai alle configurazioni e attiva quella necessaria.'
      });
    }
    
    // Check for configurations with errors
    if (stats.errorConfigs > 0) {
      tips.push({
        type: 'warning',
        icon: '⚠️',
        title: `${stats.errorConfigs} Configurazione/i con Errori`,
        message: 'Alcune configurazioni hanno problemi di connessione.',
        action: 'Controlla i dettagli degli errori e aggiorna le credenziali se necessario.'
      });
    }
    
    // Check for high unread emails
    const unreadPercentage = stats.emailsToday > 0 ? (stats.emailsUnread / stats.emailsToday) * 100 : 0;
    if (unreadPercentage > 20 && stats.emailsToday > 0) {
      tips.push({
        type: 'warning',
        icon: '⚠️',
        title: 'Molte Email Non Processate',
        message: `${Math.round(unreadPercentage)}% delle email di oggi non sono state processate.`,
        action: 'Controlla i log per identificare i problemi di processing.'
      });
    }
    
    // Check for no emails today (only if it's not early morning)
    const currentHour = new Date().getHours();
    if (stats.emailsToday === 0 && currentHour > 9) {
      tips.push({
        type: 'info',
        icon: 'ℹ️',
        title: 'Nessuna Email Oggi',
        message: 'Non sono state ricevute email oggi.',
        action: 'Verifica che le configurazioni siano corrette e che ci siano email in arrivo.'
      });
    }
    
    // Check for old last email
    if (stats.lastEmailTime) {
      const lastEmailDate = new Date(stats.lastEmailTime);
      const hoursAgo = (Date.now() - lastEmailDate.getTime()) / (1000 * 60 * 60);
      
      if (hoursAgo > 24) {
        tips.push({
          type: 'warning',
          icon: '⚠️',
          title: 'Ultima Email Troppo Vecchia',
          message: `L'ultima email è stata ricevuta ${Math.round(hoursAgo)} ore fa.`,
          action: 'Verifica che le configurazioni stiano controllando correttamente le caselle email.'
        });
      }
    }
    
    // Success message when everything is fine
    if (stats.activeConfigs > 0 && stats.errorConfigs === 0 && unreadPercentage < 10) {
      tips.push({
        type: 'success',
        icon: '✅',
        title: 'Sistema Funzionante',
        message: 'Tutte le configurazioni stanno funzionando correttamente.',
        action: 'Continua il monitoraggio periodico.'
      });
    }
    
    return tips;
  };
  
  const tips = generateTips();
  
  if (tips.length === 0) {
    return null;
  }
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Consigli di Monitoraggio</h3>
        <span className="text-2xl">🔄</span>
      </div>
      
      <div className="space-y-4">
        {tips.map((tip, index) => {
          const colorClasses = {
            error: 'bg-red-50 border-red-200',
            warning: 'bg-yellow-50 border-yellow-200',
            info: 'bg-blue-50 border-blue-200',
            success: 'bg-green-50 border-green-200'
          };
          
          return (
            <div
              key={index}
              className={`p-4 rounded-lg border ${colorClasses[tip.type]}`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-xl mt-0.5 flex-shrink-0">
                  {tip.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 mb-1">
                    {tip.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    {tip.message}
                  </p>
                  <p className="text-xs text-gray-500 italic">
                    💡 {tip.action}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-2">
          📋 Controlli Raccomandati
        </h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• <strong>Giornaliero:</strong> Verifica dashboard e metriche principali</li>
          <li>• <strong>Settimanale:</strong> Analizza trend e performance</li>
          <li>• <strong>Mensile:</strong> Pulizia log e ottimizzazione configurazioni</li>
        </ul>
      </div>
    </div>
  );
}
