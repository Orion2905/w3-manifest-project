'use client';

import React, { useState, useEffect } from 'react';
import { User, CreateUserData, UpdateUserData, Role } from '@/services/userService';
import userService from '@/services/userService';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  XMarkIcon,
  UserIcon,
  EnvelopeIcon,
  LockClosedIcon,
  IdentificationIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  GlobeAmericasIcon,
  LanguageIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

interface UserFormProps {
  user?: User | null; // null for create, User object for edit
  onSuccess: (message: string) => void;
  onCancel: () => void;
  onError: (error: string) => void;
}

interface FormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  role_id: number | '';
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  department: string;
  phone: string;
  timezone: string;
  language: string;
}

interface FormErrors {
  [key: string]: string;
}

const UserForm: React.FC<UserFormProps> = ({
  user,
  onSuccess,
  onCancel,
  onError
}) => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    role_id: '',
    is_active: true,
    is_verified: false,
    is_locked: false,
    department: '',
    phone: '',
    timezone: 'UTC',
    language: 'it'
  });

  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const isEditMode = !!user;

  // Load roles
  useEffect(() => {
    const loadRoles = async () => {
      try {
        const response = await userService.getRoles();
        setRoles(response.roles);
        
        // Set default role to viewer if creating new user
        if (!isEditMode && response.roles.length > 0) {
          const viewerRole = response.roles.find(r => r.name === 'viewer');
          if (viewerRole) {
            setFormData(prev => ({ ...prev, role_id: viewerRole.id }));
          }
        }
      } catch (err) {
        console.error('Errore nel caricamento dei ruoli:', err);
      }
    };

    if (isOpen) {
      loadRoles();
    }
  }, [isOpen, isEditMode]);

  // Load user data for edit mode
  useEffect(() => {
    if (isEditMode && user) {
      setFormData({
        username: user.username,
        email: user.email,
        password: '',
        confirmPassword: '',
        first_name: user.first_name,
        last_name: user.last_name,
        role_id: (user as any).role?.id || '',
        is_active: user.is_active,
        is_verified: user.is_verified,
        is_locked: user.is_locked,
        department: user.department || '',
        phone: user.phone || '',
        timezone: user.timezone || 'UTC',
        language: user.language || 'it'
      });
    } else {
      // Reset form for create mode
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        role_id: '',
        is_active: true,
        is_verified: false,
        is_locked: false,
        department: '',
        phone: '',
        timezone: 'UTC',
        language: 'it'
      });
    }
    setErrors({});
  }, [user, isEditMode, isOpen]);

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Required fields validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username è obbligatorio';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username deve essere almeno di 3 caratteri';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
      newErrors.username = 'Username può contenere solo lettere, numeri, underscore e trattini';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email è obbligatoria';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email non valida';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Nome è obbligatorio';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Cognome è obbligatorio';
    }

    if (!formData.role_id) {
      newErrors.role_id = 'Ruolo è obbligatorio';
    }

    // Password validation (required for create, optional for edit)
    if (!isEditMode || formData.password) {
      if (!formData.password) {
        if (!isEditMode) {
          newErrors.password = 'Password è obbligatoria';
        }
      } else {
        if (formData.password.length < 8) {
          newErrors.password = 'Password deve essere almeno di 8 caratteri';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
          newErrors.password = 'Password deve contenere almeno una lettera minuscola, maiuscola e un numero';
        }

        if (formData.password !== formData.confirmPassword) {
          newErrors.confirmPassword = 'Le password non corrispondono';
        }
      }
    }

    // Email validation
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Formato email non valido';
    }

    // Phone validation (optional)
    if (formData.phone && !/^[\+]?[0-9\s\-\(\)]+$/.test(formData.phone)) {
      newErrors.phone = 'Formato telefono non valido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
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
          username: formData.username,
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role_id: formData.role_id as number,
          is_active: formData.is_active,
          is_verified: formData.is_verified,
          is_locked: formData.is_locked,
          department: formData.department || undefined,
          phone: formData.phone || undefined,
          timezone: formData.timezone,
          language: formData.language
        };

        // Only include password if it was provided
        if (formData.password) {
          updateData.password = formData.password;
        }

        const response = await userService.updateUser(user.id, updateData);
        onSave(response.user);
      } else {
        // Create user
        const createData: CreateUserData = {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role_id: formData.role_id as number,
          is_active: formData.is_active,
          is_verified: formData.is_verified,
          department: formData.department || undefined,
          phone: formData.phone || undefined
        };

        const response = await userService.createUser(createData);
        onSave(response.user);
      }

      onClose();
    } catch (err: any) {
      const errorMessage = err.message || `Errore durante ${isEditMode ? 'l\'aggiornamento' : 'la creazione'} dell'utente`;
      if (onError) {
        onError(errorMessage);
      }
      setErrors({ general: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {isEditMode ? `Modifica Utente: ${user?.username}` : 'Nuovo Utente'}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-5 w-5" />
              </Button>
            </div>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* General error */}
              {errors.general && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="text-sm text-red-700">{errors.general}</div>
                </div>
              )}

              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <UserIcon className="inline h-4 w-4 mr-1" />
                    Username *
                  </label>
                  <Input
                    type="text"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    placeholder="es. johndoe"
                    error={errors.username}
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <EnvelopeIcon className="inline h-4 w-4 mr-1" />
                    Email *
                  </label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="es. john@example.com"
                    error={errors.email}
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Password fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <LockClosedIcon className="inline h-4 w-4 mr-1" />
                    Password {!isEditMode && '*'}
                    {isEditMode && <span className="text-sm text-gray-500">(lascia vuoto per non cambiare)</span>}
                  </label>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      placeholder="••••••••"
                      error={errors.password}
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
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <LockClosedIcon className="inline h-4 w-4 mr-1" />
                    Conferma Password {!isEditMode && '*'}
                  </label>
                  <div className="relative">
                    <Input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      placeholder="••••••••"
                      error={errors.confirmPassword}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? (
                        <EyeSlashIcon className="h-4 w-4 text-gray-400" />
                      ) : (
                        <EyeIcon className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Personal Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <IdentificationIcon className="inline h-4 w-4 mr-1" />
                    Nome *
                  </label>
                  <Input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => handleInputChange('first_name', e.target.value)}
                    placeholder="es. John"
                    error={errors.first_name}
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <IdentificationIcon className="inline h-4 w-4 mr-1" />
                    Cognome *
                  </label>
                  <Input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => handleInputChange('last_name', e.target.value)}
                    placeholder="es. Doe"
                    error={errors.last_name}
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Role and Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Ruolo *
                  </label>
                  <select
                    value={formData.role_id}
                    onChange={(e) => handleInputChange('role_id', parseInt(e.target.value))}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                      errors.role_id ? 'border-red-300' : 'border-gray-300'
                    }`}
                    disabled={loading}
                  >
                    <option value="">Seleziona un ruolo</option>
                    {roles.map(role => (
                      <option key={role.id} value={role.id}>
                        {role.display_name} - {role.description}
                      </option>
                    ))}
                  </select>
                  {errors.role_id && (
                    <p className="mt-1 text-sm text-red-600">{errors.role_id}</p>
                  )}
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Stato Account
                  </label>
                  
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_active}
                        onChange={(e) => handleInputChange('is_active', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                        disabled={loading}
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Attivo</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_verified}
                        onChange={(e) => handleInputChange('is_verified', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                        disabled={loading}
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Verificato</span>
                    </label>

                    {isEditMode && (
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.is_locked}
                          onChange={(e) => handleInputChange('is_locked', e.target.checked)}
                          className="rounded border-gray-300 text-red-600 focus:ring-red-500 dark:border-gray-600 dark:bg-gray-700"
                          disabled={loading}
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Bloccato</span>
                      </label>
                    )}
                  </div>
                </div>
              </div>

              {/* Additional Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <BuildingOfficeIcon className="inline h-4 w-4 mr-1" />
                    Dipartimento
                  </label>
                  <Input
                    type="text"
                    value={formData.department}
                    onChange={(e) => handleInputChange('department', e.target.value)}
                    placeholder="es. IT, HR, Marketing"
                    error={errors.department}
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <PhoneIcon className="inline h-4 w-4 mr-1" />
                    Telefono
                  </label>
                  <Input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    placeholder="es. +39 123 456 7890"
                    error={errors.phone}
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <GlobeAmericasIcon className="inline h-4 w-4 mr-1" />
                    Fuso Orario
                  </label>
                  <select
                    value={formData.timezone}
                    onChange={(e) => handleInputChange('timezone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    disabled={loading}
                  >
                    <option value="UTC">UTC</option>
                    <option value="Europe/Rome">Europe/Rome</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="America/Los_Angeles">America/Los_Angeles</option>
                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <LanguageIcon className="inline h-4 w-4 mr-1" />
                    Lingua
                  </label>
                  <select
                    value={formData.language}
                    onChange={(e) => handleInputChange('language', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    disabled={loading}
                  >
                    <option value="it">Italiano</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                  </select>
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={loading}
                >
                  Annulla
                </Button>
                <Button
                  type="submit"
                  isLoading={loading}
                  className="bg-blue-600 hover:bg-blue-700"
                  disabled={loading}
                >
                  {isEditMode ? 'Salva Modifiche' : 'Crea Utente'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UserForm;
