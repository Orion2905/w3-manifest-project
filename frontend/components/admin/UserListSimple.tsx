'use client';

import React, { useState } from 'react';
import { User, Role } from '@/services/userService';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  Cog6ToothIcon,
  UserIcon,
  EnvelopeIcon,
  CalendarIcon,
  ShieldCheckIcon,
  ShieldExclamationIcon,
  LockClosedIcon,
  LockOpenIcon,
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

interface UserListProps {
  users: User[];
  loading: boolean;
  filters: {
    search: string;
    role: string;
    status: string;
    verified: string;
  };
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  onFiltersChange: (filters: any) => void;
  onPaginationChange: (page: number) => void;
  onEditUser: (user: User) => void;
  onUserActions: (user: User) => void;
  onRefresh: () => void;
}

const UserList: React.FC<UserListProps> = ({
  users,
  loading,
  filters,
  pagination,
  onFiltersChange,
  onPaginationChange,
  onEditUser,
  onUserActions,
  onRefresh
}) => {
  const [showFilters, setShowFilters] = useState(false);

  // Handle filter changes
  const handleFilterChange = (key: string, value: string) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  // Clear all filters
  const clearFilters = () => {
    onFiltersChange({
      search: '',
      role: '',
      status: '',
      verified: ''
    });
  };

  // Get status badge
  const getStatusBadge = (user: User) => {
    if (!user.is_active) {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full">Inattivo</span>;
    }
    if (user.is_locked) {
      return <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 rounded-full">Bloccato</span>;
    }
    if (!user.is_verified) {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">Non Verificato</span>;
    }
    return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">Attivo</span>;
  };

  // Get role badge
  const getRoleBadge = (user: User) => {
    const roleColors = {
      admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      manager: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      viewer: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    };
    
    const colorClass = roleColors[user.role as keyof typeof roleColors] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colorClass}`}>
        {user.role_display}
      </span>
    );
  };

  return (
    <Card>
      <CardHeader className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Lista Utenti ({pagination.total})
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              Filtri
            </Button>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <Input
                type="text"
                placeholder="Cerca utenti..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-9 w-64"
              />
            </div>
            <Button variant="outline" onClick={onRefresh} disabled={loading}>
              Aggiorna
            </Button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Ruolo
                </label>
                <select
                  value={filters.role}
                  onChange={(e) => handleFilterChange('role', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Tutti i ruoli</option>
                  <option value="admin">Amministratore</option>
                  <option value="manager">Manager</option>
                  <option value="viewer">Visualizzatore</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Stato
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Tutti gli stati</option>
                  <option value="active">Attivo</option>
                  <option value="inactive">Inattivo</option>
                  <option value="locked">Bloccato</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Verifica
                </label>
                <select
                  value={filters.verified}
                  onChange={(e) => handleFilterChange('verified', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Tutti</option>
                  <option value="verified">Verificati</option>
                  <option value="unverified">Non verificati</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4 flex justify-end">
              <Button variant="outline" onClick={clearFilters}>
                Pulisci Filtri
              </Button>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent className="p-0">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-500 dark:text-gray-400">Caricamento...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center">
            <UserIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Nessun utente trovato
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Non ci sono utenti che corrispondono ai criteri di ricerca.
            </p>
          </div>
        ) : (
          <>
            {/* Desktop Table View */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Utente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Ruolo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Stato
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Ultimo Accesso
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Azioni
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                                {user.first_name[0]}{user.last_name[0]}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {user.full_name}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
                              <EnvelopeIcon className="h-3 w-3 mr-1" />
                              {user.email}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              @{user.username}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getRoleBadge(user)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(user)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {user.last_login ? (
                          <div className="flex items-center">
                            <CalendarIcon className="h-3 w-3 mr-1" />
                            {new Date(user.last_login).toLocaleDateString('it-IT')}
                          </div>
                        ) : (
                          'Mai'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onEditUser(user)}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onUserActions(user)}
                            className="text-gray-600 hover:text-gray-700"
                          >
                            <Cog6ToothIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Card View */}
            <div className="lg:hidden divide-y divide-gray-200 dark:divide-gray-700">
              {users.map((user) => (
                <div key={user.id} className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                          {user.first_name[0]}{user.last_name[0]}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {user.full_name}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {user.email}
                      </div>
                      <div className="mt-1 flex items-center space-x-2">
                        {getRoleBadge(user)}
                        {getStatusBadge(user)}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onEditUser(user)}
                      >
                        <PencilIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onUserActions(user)}
                      >
                        <Cog6ToothIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Mostra{' '}
                    <span className="font-medium">{(pagination.page - 1) * pagination.limit + 1}</span>{' '}
                    a{' '}
                    <span className="font-medium">
                      {Math.min(pagination.page * pagination.limit, pagination.total)}
                    </span>{' '}
                    di <span className="font-medium">{pagination.total}</span> risultati
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onPaginationChange(pagination.page - 1)}
                      disabled={pagination.page <= 1}
                    >
                      <ChevronLeftIcon className="h-4 w-4" />
                    </Button>
                    
                    {[...Array(pagination.totalPages)].map((_, index) => {
                      const pageNumber = index + 1;
                      if (
                        pageNumber === 1 ||
                        pageNumber === pagination.totalPages ||
                        (pageNumber >= pagination.page - 2 && pageNumber <= pagination.page + 2)
                      ) {
                        return (
                          <Button
                            key={pageNumber}
                            variant={pageNumber === pagination.page ? "primary" : "outline"}
                            size="sm"
                            onClick={() => onPaginationChange(pageNumber)}
                          >
                            {pageNumber}
                          </Button>
                        );
                      }
                      return null;
                    })}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onPaginationChange(pagination.page + 1)}
                      disabled={pagination.page >= pagination.totalPages}
                    >
                      <ChevronRightIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default UserList;
