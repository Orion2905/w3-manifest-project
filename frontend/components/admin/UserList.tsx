'use client';

import React, { useState, useEffect } from 'react';
import { User, UserFilters, PaginatedUsersResponse, Role } from '@/services/userService';
import userService from '@/services/userService';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  UserIcon,
  EnvelopeIcon,
  CalendarIcon,
  ShieldCheckIcon,
  ShieldExclamationIcon,
  LockClosedIcon,
  LockOpenIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';

interface UserListProps {
  users?: User[];
  loading?: boolean;
  filters?: {
    search: string;
    role: string;
    status: string;
    verified: string;
  };
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  onFiltersChange?: (filters: any) => void;
  onPaginationChange?: (page: number) => void;
  onEditUser?: (user: User) => void;
  onUserActions?: (user: User) => void;
  onRefresh?: () => void;
  onUserSelect?: (user: User) => void;
  onUserDelete?: (user: User) => void;
  onCreateUser?: () => void;
  refreshTrigger?: number;
}

const UserList: React.FC<UserListProps> = ({
  users: propUsers,
  loading: propLoading = false,
  filters: propFilters,
  pagination: propPagination,
  onFiltersChange,
  onPaginationChange,
  onEditUser,
  onUserActions,
  onRefresh,
  onUserSelect,
  onUserDelete,
  onCreateUser,
  refreshTrigger = 0
}) => {
  const [users, setUsers] = useState<User[]>(propUsers || []);
  const [loading, setLoading] = useState(!propUsers);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState(propPagination || {
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  });
  // Filters state - use props if available, otherwise internal state
  const [filters, setFilters] = useState<UserFilters>(propFilters || {
    search: '',
    role: '',
    status: '',
    verified: ''
  });

  // Sync with props
  useEffect(() => {
    if (propUsers) {
      setUsers(propUsers);
      setLoading(propLoading);
    }
  }, [propUsers, propLoading]);

  useEffect(() => {
    if (propFilters) {
      setFilters(propFilters);
    }
  }, [propFilters]);

  useEffect(() => {
    if (propPagination) {
      setPagination({
        page: propPagination.page,
        per_page: propPagination.limit,
        total: propPagination.total,
        pages: propPagination.totalPages,
        has_next: propPagination.page < propPagination.totalPages,
        has_prev: propPagination.page > 1
      });
    }
  }, [propPagination]);
  const [filters, setFilters] = useState<UserFilters>({
    search: '',
    role: '',
    status: undefined,
    page: 1,
    per_page: 20
  });
  
  const [roles, setRoles] = useState<Role[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Load users
  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await userService.getUsers(filters);
      setUsers(response.users);
      setPagination(response.pagination);
    } catch (err: any) {
      setError(err.message || 'Errore durante il caricamento degli utenti');
    } finally {
      setLoading(false);
    }
  };

  // Load roles for filter
  const loadRoles = async () => {
    try {
      const response = await userService.getRoles();
      setRoles(response.roles);
    } catch (err) {
      console.error('Errore nel caricamento dei ruoli:', err);
    }
  };

  // Initial load
  useEffect(() => {
    loadUsers();
    loadRoles();
  }, []);

  // Reload when filters change
  useEffect(() => {
    loadUsers();
  }, [filters]);

  // Reload when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger > 0) {
      loadUsers();
    }
  }, [refreshTrigger]);

  // Handle search
  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value, page: 1 }));
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof UserFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  // Handle pagination
  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  // Toggle user status
  const handleToggleStatus = async (user: User) => {
    try {
      await userService.toggleUserStatus(user.id);
      loadUsers(); // Refresh list
    } catch (err: any) {
      setError(err.message || 'Errore durante il cambio di stato');
    }
  };

  // Status badge component
  const StatusBadge: React.FC<{ user: User }> = ({ user }) => {
    if (user.is_locked) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
          <LockClosedIcon className="w-3 h-3 mr-1" />
          Bloccato
        </span>
      );
    }
    
    if (!user.is_active) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400">
          <ShieldExclamationIcon className="w-3 h-3 mr-1" />
          Inattivo
        </span>
      );
    }
    
    if (!user.is_verified) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
          <ShieldExclamationIcon className="w-3 h-3 mr-1" />
          Non verificato
        </span>
      );
    }
    
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
        <ShieldCheckIcon className="w-3 h-3 mr-1" />
        Attivo
      </span>
    );
  };

  // Role badge component
  const RoleBadge: React.FC<{ role: string }> = ({ role }) => {
    const colors = {
      admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      manager: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      viewer: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    };
    
    const colorClass = colors[role as keyof typeof colors] || colors.viewer;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {role === 'admin' && <ShieldCheckIcon className="w-3 h-3 mr-1" />}
        {role === 'manager' && <UserIcon className="w-3 h-3 mr-1" />}
        {role === 'viewer' && <EyeIcon className="w-3 h-3 mr-1" />}
        {role}
      </span>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with search and filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Gestione Utenti ({pagination.total})
            </h3>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center"
              >
                <FunnelIcon className="w-4 h-4 mr-1" />
                Filtri
              </Button>
              {onCreateUser && (
                <Button
                  onClick={onCreateUser}
                  className="flex items-center bg-blue-600 hover:bg-blue-700"
                >
                  <PlusIcon className="w-4 h-4 mr-1" />
                  Nuovo Utente
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Search bar */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Cerca per username, email, nome..."
              value={filters.search || ''}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Ruolo
                </label>
                <select
                  value={filters.role || ''}
                  onChange={(e) => handleFilterChange('role', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Tutti i ruoli</option>
                  {roles.map(role => (
                    <option key={role.id} value={role.name}>
                      {role.display_name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Stato
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Tutti gli stati</option>
                  <option value="active">Attivi</option>
                  <option value="inactive">Inattivi</option>
                  <option value="locked">Bloccati</option>
                  <option value="verified">Verificati</option>
                  <option value="unverified">Non verificati</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Per pagina
                </label>
                <select
                  value={filters.per_page}
                  onChange={(e) => handleFilterChange('per_page', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error message */}
      {error && (
        <Card>
          <CardContent className="p-4">
            <div className="text-red-600 dark:text-red-400 text-sm">{error}</div>
          </CardContent>
        </Card>
      )}

      {/* Users list */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Utente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Ruolo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Stato
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Ultimo accesso
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
                          <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                            <UserIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {user.full_name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            @{user.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900 dark:text-white">
                        <EnvelopeIcon className="h-4 w-4 mr-2 text-gray-400" />
                        {user.email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <RoleBadge role={user.role_name} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge user={user} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {user.last_login ? (
                        <div className="flex items-center">
                          <CalendarIcon className="h-4 w-4 mr-2" />
                          {new Date(user.last_login).toLocaleDateString('it-IT')}
                        </div>
                      ) : (
                        <span className="text-gray-400">Mai</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        {onUserSelect && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onUserSelect(user)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </Button>
                        )}
                        {onUserEdit && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onUserEdit(user)}
                            className="text-green-600 hover:text-green-800"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleStatus(user)}
                          className={user.is_active ? "text-orange-600 hover:text-orange-800" : "text-green-600 hover:text-green-800"}
                        >
                          {user.is_active ? <LockClosedIcon className="h-4 w-4" /> : <LockOpenIcon className="h-4 w-4" />}
                        </Button>
                        {onUserDelete && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onUserDelete(user)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="bg-white dark:bg-gray-900 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={!pagination.has_prev}
                >
                  Precedente
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={!pagination.has_next}
                >
                  Successivo
                </Button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Mostra{' '}
                    <span className="font-medium">{(pagination.page - 1) * pagination.per_page + 1}</span>{' '}
                    a{' '}
                    <span className="font-medium">
                      {Math.min(pagination.page * pagination.per_page, pagination.total)}
                    </span>{' '}
                    di{' '}
                    <span className="font-medium">{pagination.total}</span>{' '}
                    risultati
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={!pagination.has_prev}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium text-gray-500 hover:bg-gray-50"
                    >
                      Precedente
                    </Button>
                    {[...Array(pagination.pages)].map((_, index) => {
                      const page = index + 1;
                      const isCurrentPage = page === pagination.page;
                      return (
                        <Button
                          key={page}
                          variant={isCurrentPage ? "primary" : "outline"}
                          onClick={() => handlePageChange(page)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            isCurrentPage
                              ? 'z-10 bg-blue-600 border-blue-600 text-white'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </Button>
                      );
                    })}
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={!pagination.has_next}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium text-gray-500 hover:bg-gray-50"
                    >
                      Successivo
                    </Button>
                  </nav>
                </div>
              </div>
            </div>
          )}

          {/* Empty state */}
          {users.length === 0 && !loading && (
            <div className="text-center py-12">
              <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Nessun utente trovato</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {filters.search || filters.role || filters.status
                  ? 'Prova a cambiare i filtri di ricerca.'
                  : 'Inizia creando il primo utente.'}
              </p>
              {onCreateUser && !filters.search && !filters.role && !filters.status && (
                <div className="mt-6">
                  <Button onClick={onCreateUser} className="bg-blue-600 hover:bg-blue-700">
                    <PlusIcon className="w-4 h-4 mr-1" />
                    Crea primo utente
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UserList;
