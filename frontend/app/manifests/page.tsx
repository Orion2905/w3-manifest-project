'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { manifestService } from '@/services/manifest';
import { ManifestEmail } from '@/types/manifest';
import { PaginatedResponse } from '@/types/api';
import Link from 'next/link';

export default function ManifestsPage() {
  const [manifests, setManifests] = useState<ManifestEmail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });

  const loadManifests = async (page: number = 1) => {
    try {
      setLoading(true);
      const response: PaginatedResponse<ManifestEmail> = await manifestService.getManifestEmails(page, pagination.limit);
      
      setManifests(response.data);
      setPagination({
        page: response.page,
        limit: response.limit,
        total: response.total,
        totalPages: response.totalPages
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load manifests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadManifests();
  }, []);

  const handlePageChange = (newPage: number) => {
    loadManifests(newPage);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'processed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Manifests</h1>
        <Link href="/upload">
          <Button>Upload New Manifest</Button>
        </Link>
      </div>

      {/* Manifests Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">
              Manifest History ({pagination.total})
            </h3>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading manifests...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-600">{error}</div>
          ) : manifests.length === 0 ? (
            <div className="text-center py-8 text-gray-600">
              <div className="space-y-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>No manifests found.</p>
                <Link href="/upload">
                  <Button>Upload Your First Manifest</Button>
                </Link>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subject
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sender
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Services Found
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Orders Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Received
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {manifests.map((manifest) => (
                    <tr key={manifest.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {manifest.subject}
                        </div>
                        <div className="text-sm text-gray-500">
                          {manifest.original_filename}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {manifest.sender}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(manifest.status)}`}>
                          {manifest.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {manifest.services_found}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            manifest.orders_created > 0 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {manifest.orders_created}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div>
                          {new Date(manifest.received_at).toLocaleDateString()}
                        </div>
                        <div className="text-xs">
                          {new Date(manifest.received_at).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link
                          href={`/manifests/${manifest.id}`}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          View
                        </Link>
                        {manifest.status === 'failed' && (
                          <button
                            onClick={() => {/* Retry processing */}}
                            className="text-green-600 hover:text-green-900"
                          >
                            Retry
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Processing Errors */}
      {manifests.some(m => m.processing_errors.length > 0) && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-red-900">Processing Errors</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {manifests
                .filter(m => m.processing_errors.length > 0)
                .map((manifest) => (
                  <div key={manifest.id} className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="font-medium text-red-900">
                      {manifest.subject}
                    </div>
                    <ul className="mt-2 text-sm text-red-700 space-y-1">
                      {manifest.processing_errors.map((error, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2">•</span>
                          {error}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-700">
            Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} results
          </div>
          
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
            >
              Previous
            </Button>
            
            <span className="flex items-center px-4 py-2 text-sm text-gray-700">
              Page {pagination.page} of {pagination.totalPages}
            </span>
            
            <Button
              variant="outline"
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
