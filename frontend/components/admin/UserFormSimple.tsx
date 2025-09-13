'use client';

import React, { useState, useEffect } from 'react';
import { User, CreateUserData, UpdateUserData, Role } from '@/services/userService';
import userService from '@/services/userService';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  UserIcon,
  EnvelopeIcon,
  LockClosedIcon,
  IdentificationIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

interface UserFormProps {
  user?: User | null;
  onSuccess: (message: string) => void;
  onCancel: () => void;
  onError: (error: string) => void;
}

interface FormData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role_id: number | '';
  department: string;
  phone: string;
  timezone: string;
  language: string;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  password: string;
  confirm_password: string;
}

const UserFormSimple: React.FC<UserFormProps> = ({
  user,
  onSuccess,
  onCancel,
  onError
}) => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role_id: '',
    department: '',
    phone: '',
    timezone: 'Europe/Rome',
    language: 'it',
    is_active: true,
    is_verified: false,
    is_locked: false,
    password: '',
    confirm_password: ''
  });

  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const isEditMode = !!user;

  // Load initial data
  useEffect(() => {
    loadRoles();
    
    if (user) {
      setFormData({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        role_id: (user.role as any)?.id || '',
        department: user.department || '',
        phone: user.phone || '',
        timezone: user.timezone || 'Europe/Rome',
        language: user.language || 'it',
        is_active: user.is_active,
        is_verified: user.is_verified,
        is_locked: user.is_locked,
        password: '',
        confirm_password: ''
      });
    }
  }, [user]);

  // Load roles
  const loadRoles = async () => {
    try {
      const response = await userService.getRoles();
      setRoles(response.roles);
    } catch (err: any) {
      console.error('Error loading roles:', err);
      onError('Errore durante il caricamento dei ruoli');
    }
  };

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  // Generate random password
  const generatePassword = () => {
    const length = 12;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    setFormData(prev => ({ 
      ...prev, 
      password, 
      confirm_password: password 
    }));
  };

  // Validate form
  const validateForm = (): boolean => {
    if (!formData.username.trim()) {
      onError('Username è richiesto');
      return false;
    }
    
    if (!formData.email.trim()) {
      onError('Email è richiesta');
      return false;
    }
    
    if (!formData.first_name.trim()) {
      onError('Nome è richiesto');
      return false;
    }
    
    if (!formData.last_name.trim()) {
      onError('Cognome è richiesto');
      return false;
    }
    
    if (!formData.role_id) {
      onError('Ruolo è richiesto');
      return false;
    }

    if (!isEditMode) {
      if (!formData.password) {
        onError('Password è richiesta per i nuovi utenti');
        return false;
      }
      
      if (formData.password.length < 8) {
        onError('La password deve essere almeno di 8 caratteri');
        return false;
      }
      
      if (formData.password !== formData.confirm_password) {
        onError('Le password non corrispondono');
        return false;
      }
    } else {
      // In edit mode, only validate password if it's being changed
      if (formData.password && formData.password.length < 8) {
        onError('La password deve essere almeno di 8 caratteri');
        return false;
      }
      
      if (formData.password && formData.password !== formData.confirm_password) {
        onError('Le password non corrispondono');
        return false;
      }
    }
    
    return true;
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      if (isEditMode && user) {
        // Update user
        const updateData: UpdateUserData = {
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role_id: Number(formData.role_id),
          is_active: formData.is_active,
          is_verified: formData.is_verified,
          is_locked: formData.is_locked,
          department: formData.department || undefined,
          phone: formData.phone || undefined,
          timezone: formData.timezone,
          language: formData.language
        };

        // Only include password if it's being changed
        if (formData.password) {
          (updateData as any).password = formData.password;
        }

        const response = await userService.updateUser(user.id, updateData);
        onSuccess(`Utente ${response.user.username} aggiornato con successo`);
      } else {
        // Create user
        const createData: CreateUserData = {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role_id: Number(formData.role_id),
          is_active: formData.is_active,
          is_verified: formData.is_verified,
          department: formData.department || undefined,
          phone: formData.phone || undefined
        };

        const response = await userService.createUser(createData);
        onSuccess(`Utente ${response.user.username} creato con successo`);
      }
    } catch (err: any) {
      onError(err.message || 'Errore durante il salvataggio dell\'utente');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nome *
              </label>
              <div className="relative">
                <UserIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="Nome"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Cognome *
              </label>
              <div className="relative">
                <UserIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="Cognome"
                  required
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          {/* Username and Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Username *
              </label>
              <div className="relative">
                <IdentificationIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="Username"
                  required
                  disabled={loading || isEditMode}
                />
              </div>
              {isEditMode && (
                <p className="text-xs text-gray-500 mt-1">Lo username non può essere modificato</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email *
              </label>
              <div className="relative">
                <EnvelopeIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="email@esempio.com"
                  required
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          {/* Role */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Ruolo *
            </label>
            <select
              name="role_id"
              value={formData.role_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              required
              disabled={loading}
            >
              <option value="">Seleziona un ruolo</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.display_name}
                </option>
              ))}
            </select>
          </div>

          {/* Password */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password {!isEditMode && '*'}
              </label>
              <div className="relative">
                <LockClosedIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-9 pr-20"
                  placeholder={isEditMode ? 'Lascia vuoto per non modificare' : 'Password'}
                  required={!isEditMode}
                  disabled={loading}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex space-x-1">
                  <button
                    type="button"
                    onClick={generatePassword}
                    className="text-xs text-blue-600 hover:text-blue-700"
                    disabled={loading}
                  >
                    Genera
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-4 w-4" />
                    ) : (
                      <EyeIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Conferma Password {!isEditMode && '*'}
              </label>
              <div className="relative">
                <LockClosedIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirm_password"
                  value={formData.confirm_password}
                  onChange={handleInputChange}
                  className="pl-9 pr-9"
                  placeholder="Conferma password"
                  required={!isEditMode && !!formData.password}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-4 w-4" />
                  ) : (
                    <EyeIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Dipartimento
              </label>
              <div className="relative">
                <BuildingOfficeIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="Dipartimento"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Telefono
              </label>
              <div className="relative">
                <PhoneIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="pl-9"
                  placeholder="+39 123 456 7890"
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          {/* Status Options */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Stato Utente
            </h4>
            
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  disabled={loading}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Utente attivo (può accedere al sistema)
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_verified"
                  checked={formData.is_verified}
                  onChange={handleInputChange}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  disabled={loading}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Email verificata
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_locked"
                  checked={formData.is_locked}
                  onChange={handleInputChange}
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  disabled={loading}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Account bloccato
                </span>
              </label>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
            >
              Annulla
            </Button>
            
            <Button
              type="submit"
              isLoading={loading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isEditMode ? 'Aggiorna Utente' : 'Crea Utente'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default UserFormSimple;
