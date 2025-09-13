'use client';

import React, { useState } from 'react';
import { User } from '@/services/userService';
import userService from '@/services/userService';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  XMarkIcon,
  LockClosedIcon,
  LockOpenIcon,
  TrashIcon,
  KeyIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

interface UserActionsProps {
  user: User;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (message: string) => void;
  onError: (error: string) => void;
}

type ActionType = 'toggle-status' | 'delete' | 'reset-password' | 'view-details';

const UserActions: React.FC<UserActionsProps> = ({
  user,
  isOpen,
  onClose,
  onSuccess,
  onError
}) => {
  const [selectedAction, setSelectedAction] = useState<ActionType | null>(null);
  const [loading, setLoading] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [confirmAction, setConfirmAction] = useState(false);

  // Handle action selection
  const handleActionSelect = (action: ActionType) => {
    setSelectedAction(action);
    setConfirmAction(false);
    setNewPassword('');
  };

  // Handle toggle status
  const handleToggleStatus = async () => {
    if (!confirmAction) {
      setConfirmAction(true);
      return;
    }

    setLoading(true);
    try {
      const response = await userService.toggleUserStatus(user.id);
      onSuccess(response.message);
      onClose();
    } catch (err: any) {
      onError(err.message || 'Errore durante il cambio di stato');
    } finally {
      setLoading(false);
    }
  };

  // Handle delete user
  const handleDeleteUser = async () => {
    if (!confirmAction) {
      setConfirmAction(true);
      return;
    }

    setLoading(true);
    try {
      const response = await userService.deleteUser(user.id);
      onSuccess(response.message);
      onClose();
    } catch (err: any) {
      onError(err.message || 'Errore durante l\'eliminazione dell\'utente');
    } finally {
      setLoading(false);
    }
  };

  // Generate random password
  const generateRandomPassword = () => {
    const length = 12;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    setNewPassword(password);
  };

  // Handle password reset
  const handleResetPassword = async () => {
    if (!newPassword.trim()) {
      onError('La password non può essere vuota');
      return;
    }

    if (newPassword.length < 8) {
      onError('La password deve essere almeno di 8 caratteri');
      return;
    }

    if (!confirmAction) {
      setConfirmAction(true);
      return;
    }

    setLoading(true);
    try {
      const response = await userService.resetPassword(user.id, newPassword);
      onSuccess(`${response.message}. Nuova password: ${newPassword}`);
      onClose();
    } catch (err: any) {
      onError(err.message || 'Errore durante il reset della password');
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setSelectedAction(null);
    setConfirmAction(false);
    setNewPassword('');
    setShowPassword(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full">
        <Card>
          <CardContent className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Azioni Utente: {user.username}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  resetForm();
                  onClose();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-5 w-5" />
              </Button>
            </div>

            {/* User info */}
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 h-10 w-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 dark:text-blue-400 font-medium">
                    {user.first_name[0]}{user.last_name[0]}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.full_name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {user.email} • {user.role_display}
                  </p>
                </div>
              </div>
            </div>

            {/* Action selection */}
            {!selectedAction && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Seleziona un'azione:
                </h4>

                {/* View Details */}
                <Button
                  variant="outline"
                  onClick={() => handleActionSelect('view-details')}
                  className="w-full justify-start text-left"
                >
                  <EyeIcon className="h-4 w-4 mr-3" />
                  <div>
                    <div className="font-medium">Visualizza Dettagli</div>
                    <div className="text-sm text-gray-500">Mostra informazioni complete dell'utente</div>
                  </div>
                </Button>

                {/* Toggle Status */}
                <Button
                  variant="outline"
                  onClick={() => handleActionSelect('toggle-status')}
                  className="w-full justify-start text-left"
                >
                  {user.is_active ? (
                    <LockClosedIcon className="h-4 w-4 mr-3 text-orange-500" />
                  ) : (
                    <LockOpenIcon className="h-4 w-4 mr-3 text-green-500" />
                  )}
                  <div>
                    <div className="font-medium">
                      {user.is_active ? 'Disattiva Utente' : 'Attiva Utente'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {user.is_active 
                        ? 'L\'utente non potrà più accedere al sistema' 
                        : 'L\'utente potrà nuovamente accedere al sistema'}
                    </div>
                  </div>
                </Button>

                {/* Reset Password */}
                <Button
                  variant="outline"
                  onClick={() => handleActionSelect('reset-password')}
                  className="w-full justify-start text-left"
                >
                  <KeyIcon className="h-4 w-4 mr-3 text-blue-500" />
                  <div>
                    <div className="font-medium">Reset Password</div>
                    <div className="text-sm text-gray-500">Imposta una nuova password per l'utente</div>
                  </div>
                </Button>

                {/* Delete User */}
                <Button
                  variant="outline"
                  onClick={() => handleActionSelect('delete')}
                  className="w-full justify-start text-left border-red-200 hover:border-red-300 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20"
                >
                  <TrashIcon className="h-4 w-4 mr-3 text-red-500" />
                  <div>
                    <div className="font-medium text-red-600 dark:text-red-400">Elimina Utente</div>
                    <div className="text-sm text-gray-500">Disattiva permanentemente l'utente</div>
                  </div>
                </Button>
              </div>
            )}

            {/* View Details */}
            {selectedAction === 'view-details' && (
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  Dettagli Utente
                </h4>
                
                <div className="space-y-3 text-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">ID:</span>
                    <span className="text-gray-900 dark:text-white">{user.id}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Username:</span>
                    <span className="text-gray-900 dark:text-white">{user.username}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Email:</span>
                    <span className="text-gray-900 dark:text-white">{user.email}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Nome completo:</span>
                    <span className="text-gray-900 dark:text-white">{user.full_name}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Ruolo:</span>
                    <span className="text-gray-900 dark:text-white">{user.role_display}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Stato:</span>
                    <span className={`${user.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {user.is_active ? 'Attivo' : 'Inattivo'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Verificato:</span>
                    <span className={`${user.is_verified ? 'text-green-600' : 'text-yellow-600'}`}>
                      {user.is_verified ? 'Sì' : 'No'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Bloccato:</span>
                    <span className={`${user.is_locked ? 'text-red-600' : 'text-green-600'}`}>
                      {user.is_locked ? 'Sì' : 'No'}
                    </span>
                  </div>
                  {user.department && (
                    <div className="grid grid-cols-2 gap-2">
                      <span className="text-gray-500">Dipartimento:</span>
                      <span className="text-gray-900 dark:text-white">{user.department}</span>
                    </div>
                  )}
                  {user.phone && (
                    <div className="grid grid-cols-2 gap-2">
                      <span className="text-gray-500">Telefono:</span>
                      <span className="text-gray-900 dark:text-white">{user.phone}</span>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-gray-500">Creato:</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(user.created_at).toLocaleDateString('it-IT')}
                    </span>
                  </div>
                  {user.last_login && (
                    <div className="grid grid-cols-2 gap-2">
                      <span className="text-gray-500">Ultimo accesso:</span>
                      <span className="text-gray-900 dark:text-white">
                        {new Date(user.last_login).toLocaleDateString('it-IT')}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex justify-end space-x-2 pt-4">
                  <Button variant="outline" onClick={resetForm}>
                    Indietro
                  </Button>
                </div>
              </div>
            )}

            {/* Toggle Status Action */}
            {selectedAction === 'toggle-status' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
                  <div>
                    <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                      {user.is_active ? 'Disattivare l\'utente?' : 'Attivare l\'utente?'}
                    </h4>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      {user.is_active 
                        ? 'L\'utente non potrà più accedere al sistema fino a quando non verrà riattivato.'
                        : 'L\'utente potrà nuovamente accedere al sistema.'}
                    </p>
                  </div>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={resetForm} disabled={loading}>
                    Annulla
                  </Button>
                  <Button
                    onClick={handleToggleStatus}
                    isLoading={loading}
                    className={`${
                      confirmAction 
                        ? 'bg-red-600 hover:bg-red-700' 
                        : user.is_active 
                          ? 'bg-orange-600 hover:bg-orange-700'
                          : 'bg-green-600 hover:bg-green-700'
                    }`}
                  >
                    {confirmAction 
                      ? 'Conferma' 
                      : user.is_active 
                        ? 'Disattiva' 
                        : 'Attiva'}
                  </Button>
                </div>
              </div>
            )}

            {/* Reset Password Action */}
            {selectedAction === 'reset-password' && (
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  Reset Password per {user.username}
                </h4>

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Nuova Password
                    </label>
                    <div className="flex space-x-2">
                      <div className="relative flex-1">
                        <Input
                          type={showPassword ? 'text' : 'password'}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Inserisci la nuova password"
                          disabled={loading}
                        />
                        <button
                          type="button"
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? (
                            <EyeSlashIcon className="h-4 w-4 text-gray-400" />
                          ) : (
                            <EyeIcon className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                      <Button
                        variant="outline"
                        onClick={generateRandomPassword}
                        disabled={loading}
                        className="px-3"
                      >
                        Genera
                      </Button>
                    </div>
                  </div>

                  {confirmAction && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <p className="text-sm text-red-700 dark:text-red-300">
                        ⚠️ Confermi di voler cambiare la password? L'utente dovrà usare la nuova password al prossimo accesso.
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={resetForm} disabled={loading}>
                    Annulla
                  </Button>
                  <Button
                    onClick={handleResetPassword}
                    isLoading={loading}
                    className={`${confirmAction ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                    disabled={!newPassword.trim()}
                  >
                    {confirmAction ? 'Conferma Reset' : 'Reset Password'}
                  </Button>
                </div>
              </div>
            )}

            {/* Delete User Action */}
            {selectedAction === 'delete' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                  <div>
                    <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
                      Eliminare l'utente?
                    </h4>
                    <p className="text-sm text-red-700 dark:text-red-300">
                      Questa azione disattiverà permanentemente l'utente. L'utente non potrà più accedere al sistema.
                      Questa operazione non può essere annullata.
                    </p>
                  </div>
                </div>

                {confirmAction && (
                  <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <p className="text-sm text-red-800 dark:text-red-200 font-medium">
                      ⚠️ Confermi di voler eliminare definitivamente l'utente "{user.username}"?
                    </p>
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={resetForm} disabled={loading}>
                    Annulla
                  </Button>
                  <Button
                    onClick={handleDeleteUser}
                    isLoading={loading}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {confirmAction ? 'Conferma Eliminazione' : 'Elimina Utente'}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UserActions;
