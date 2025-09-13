'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Button from '@/components/ui/Button';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { manifestService } from '@/services/manifest';
import { ParseManifestResponse } from '@/types/manifest';

export default function UploadPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<ParseManifestResponse | null>(null);
  const [error, setError] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const result = await manifestService.parseManifest(file);
      setUploadResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to upload and parse manifest');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    multiple: false
  });

  const handleCreateOrders = async () => {
    if (!uploadResult) return;

    try {
      // Here we would call an API to create orders from the parsed services
      // For now, just show a success message
      alert(`${uploadResult.valid_services} orders will be created from the manifest!`);
    } catch (err: any) {
      setError(err.message || 'Failed to create orders');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Upload Manifest</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Upload Document</h3>
            <p className="text-sm text-gray-600">
              Upload a Word document (.docx or .doc) containing manifest data
            </p>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-blue-400 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              
              <div className="space-y-4">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                
                {isDragActive ? (
                  <p className="text-blue-600">Drop the file here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600">
                      Drag 'n' drop a manifest file here, or click to select
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Supports .docx and .doc files
                    </p>
                  </div>
                )}
              </div>
            </div>

            {isUploading && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center px-4 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing manifest...
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        {uploadResult && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-medium text-gray-900">Parse Results</h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {uploadResult.total_services}
                  </div>
                  <div className="text-sm text-blue-800">Total Services</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {uploadResult.valid_services}
                  </div>
                  <div className="text-sm text-green-800">Valid Services</div>
                </div>
              </div>

              {uploadResult.invalid_services > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-red-800">
                    {uploadResult.invalid_services} services have validation errors
                  </div>
                </div>
              )}

              {uploadResult.errors.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-red-800">Parsing Errors:</h4>
                  <ul className="text-sm text-red-700 space-y-1">
                    {uploadResult.errors.map((error, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">•</span>
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="pt-4 border-t">
                <Button
                  onClick={handleCreateOrders}
                  className="w-full"
                  disabled={uploadResult.valid_services === 0}
                >
                  Create {uploadResult.valid_services} Orders
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Services Preview */}
      {uploadResult && uploadResult.services.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Services Preview</h3>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Service ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Passengers
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {uploadResult.services.slice(0, 10).map((service, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {service.service_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          service.action === 'new' ? 'bg-green-100 text-green-800' :
                          service.action === 'change' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {service.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {service.service_date}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                        {service.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {service.passenger_count_adults + service.passenger_count_children}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {uploadResult.services.length > 10 && (
                <div className="px-6 py-4 text-sm text-gray-500 text-center border-t">
                  Showing 10 of {uploadResult.services.length} services
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
