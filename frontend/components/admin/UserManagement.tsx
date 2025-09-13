'use client';

import React, { useState, useEffect } from 'react';
import { User, UserStats } from '@/services/userService';
import userService from '@/services/userService';
import UserList from './UserListSimple';
import UserForm from './UserFormSimple';
import UserActions from './UserActions';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { 
  PlusIcon, 
  UsersIcon, 
  UserGroupIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface UserManagementProps {
  className?: string;
}

type ViewMode = 'list' | 'create' | 'edit';

const UserManagement: React.FC<UserManagementProps> = ({ className = '' }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // View states
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserActions, setShowUserActions] = useState(false);

  // Filters and pagination
  const [filters, setFilters] = useState({
    search: '',
    role: '',
    status: '',
    verified: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  });

  // Load initial data
  useEffect(() => {
    loadUsers();
    loadStats();
  }, [filters, pagination.page, pagination.limit]);

  // Load users with filters and pagination
  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await userService.getUsers({
        ...filters,
        page: pagination.page,
        limit: pagination.limit
      });
      
      setUsers(response.users);
      setPagination(prev => ({
        ...prev,
        total: response.total,
        totalPages: response.total_pages
      }));
    } catch (err: any) {
      setError(err.message || 'Errore durante il caricamento degli utenti');
    } finally {
      setLoading(false);
    }
  };

  // Load user statistics
  const loadStats = async () => {
    try {
      const stats = await userService.getUserStats();
      setStats(stats);
    } catch (err: any) {
      console.error('Errore durante il caricamento delle statistiche:', err);
    }
  };

  // Handle user creation
  const handleCreateUser = () => {
    setSelectedUser(null);
    setViewMode('create');
  };

  // Handle user edit
  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setViewMode('edit');
  };

  // Handle user actions
  const handleUserActions = (user: User) => {
    setSelectedUser(user);
    setShowUserActions(true);
  };

  // Handle form success
  const handleFormSuccess = (message: string) => {
    setSuccess(message);
    setViewMode('list');
    setSelectedUser(null);
    loadUsers();
    loadStats();
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setViewMode('list');
    setSelectedUser(null);
  };

  // Handle actions success
  const handleActionsSuccess = (message: string) => {
    setSuccess(message);
    setShowUserActions(false);
    setSelectedUser(null);
    loadUsers();
    loadStats();
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);
  };

  // Handle actions error
  const handleActionsError = (error: string) => {
    setError(error);
    
    // Clear error message after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  // Handle filter changes
  const handleFiltersChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  // Handle pagination changes
  const handlePaginationChange = (page: number) => {
    setPagination(prev => ({ ...prev, page }));
  };

  // Clear messages
  const clearError = () => setError(null);
  const clearSuccess = () => setSuccess(null);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gestione Utenti
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gestisci gli utenti del sistema, i loro ruoli e permessi
          </p>
        </div>
        
        {viewMode === 'list' && (
          <Button onClick={handleCreateUser} className="bg-blue-600 hover:bg-blue-700">
            <PlusIcon className="h-4 w-4 mr-2" />
            Nuovo Utente
          </Button>
        )}
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={clearError}>
              ✕
            </Button>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <ShieldCheckIcon className="h-5 w-5 text-green-600 mr-2" />
              <p className="text-sm text-green-700 dark:text-green-400">{success}</p>
            </div>
            <Button variant="outline" size="sm" onClick={clearSuccess}>
              ✕
            </Button>
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      {viewMode === 'list' && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 h-8 w-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <UsersIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Utenti Totali
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.total_users}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 h-8 w-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                  <ShieldCheckIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Utenti Attivi
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.active_users}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 h-8 w-8 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Non Verificati
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.unverified_users}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 h-8 w-8 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                  <UserGroupIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Amministratori
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.role_distribution?.admin?.count || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow">
        {/* List View */}
        {viewMode === 'list' && (
          <UserList
            users={users}
            loading={loading}
            filters={filters}
            pagination={pagination}
            onFiltersChange={handleFiltersChange}
            onPaginationChange={handlePaginationChange}
            onEditUser={handleEditUser}
            onUserActions={handleUserActions}
            onRefresh={loadUsers}
          />
        )}

        {/* Create/Edit Form */}
        {(viewMode === 'create' || viewMode === 'edit') && (
          <div className="p-6">
            <div className="max-w-2xl mx-auto">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {viewMode === 'create' ? 'Crea Nuovo Utente' : 'Modifica Utente'}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {viewMode === 'create' 
                    ? 'Inserisci i dati del nuovo utente'
                    : `Modifica i dati di ${selectedUser?.username}`}
                </p>
              </div>
              
              <UserForm
                user={selectedUser}
                onSuccess={handleFormSuccess}
                onCancel={handleFormCancel}
                onError={setError}
              />
            </div>
          </div>
        )}
      </div>

      {/* User Actions Modal */}
      {showUserActions && selectedUser && (
        <UserActions
          user={selectedUser}
          isOpen={showUserActions}
          onClose={() => {
            setShowUserActions(false);
            setSelectedUser(null);
          }}
          onSuccess={handleActionsSuccess}
          onError={handleActionsError}
        />
      )}
    </div>
  );
};

export default UserManagement;
