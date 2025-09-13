'use client';

import React, { useState } from 'react';
import Button from '@/components/ui/Button';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { apiClient } from '@/services/api';

export default function ApiTestComponent() {
  const [testResults, setTestResults] = useState<any>({});
  const [isLoading, setIsLoading] = useState(false);

  const testEndpoints = [
    { name: 'Health Check', endpoint: '/health', method: 'GET' },
    { name: 'Orders List', endpoint: '/orders', method: 'GET' },
    { name: 'Manifest Stats', endpoint: '/manifest/stats', method: 'GET' },
  ];

  const runTest = async (endpoint: string, method: string, name: string) => {
    setIsLoading(true);
    try {
      let response;
      if (method === 'GET') {
        response = await apiClient.get(endpoint);
      }
      setTestResults(prev => ({
        ...prev,
        [name]: { success: true, data: response, error: null }
      }));
    } catch (error: any) {
      setTestResults(prev => ({
        ...prev,
        [name]: { success: false, data: null, error: error.message }
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const runAllTests = async () => {
    setTestResults({});
    for (const test of testEndpoints) {
      await runTest(test.endpoint, test.method, test.name);
    }
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-medium text-gray-900">API Integration Test</h3>
        <p className="text-sm text-gray-600">
          Test the connection between frontend and backend
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={runAllTests} isLoading={isLoading}>
          Run All Tests
        </Button>

        <div className="space-y-2">
          {testEndpoints.map((test) => {
            const result = testResults[test.name];
            return (
              <div
                key={test.name}
                className={`p-3 rounded-lg border ${
                  result
                    ? result.success
                      ? 'border-green-200 bg-green-50'
                      : 'border-red-200 bg-red-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-medium">{test.name}</span>
                    <span className="ml-2 text-sm text-gray-500">
                      {test.method} {test.endpoint}
                    </span>
                  </div>
                  <div className="flex items-center">
                    {result && (
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          result.success
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {result.success ? 'Success' : 'Failed'}
                      </span>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      className="ml-2"
                      onClick={() => runTest(test.endpoint, test.method, test.name)}
                    >
                      Test
                    </Button>
                  </div>
                </div>
                {result && result.error && (
                  <div className="mt-2 text-sm text-red-600">{result.error}</div>
                )}
                {result && result.success && result.data && (
                  <div className="mt-2 text-xs text-gray-600">
                    <pre>{JSON.stringify(result.data, null, 2).slice(0, 200)}...</pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
