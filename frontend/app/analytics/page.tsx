'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { orderService } from '@/services/order';
import { manifestService } from '@/services/manifest';

interface Analytics {
  orderStats: {
    total_orders: number;
    pending_orders: number;
    completed_orders: number;
    cancelled_orders: number;
    monthly_stats: Array<{ month: string; count: number }>;
  };
  manifestStats: {
    total_manifests: number;
    pending_manifests: number;
    approved_manifests: number;
    rejected_manifests: number;
    daily_stats: Array<{ date: string; count: number }>;
  };
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        const [orderStats, manifestStats] = await Promise.all([
          orderService.getOrderStats(),
          manifestService.getManifestStats()
        ]);

        setAnalytics({ orderStats, manifestStats });
      } catch (err: any) {
        setError(err.message || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        {error}
      </div>
    );
  }

  if (!analytics) return null;

  const orderCompletionRate = analytics.orderStats.total_orders > 0 
    ? ((analytics.orderStats.completed_orders / analytics.orderStats.total_orders) * 100).toFixed(1)
    : '0';

  const manifestProcessingRate = analytics.manifestStats.total_manifests > 0
    ? (((analytics.manifestStats.approved_manifests) / analytics.manifestStats.total_manifests) * 100).toFixed(1)
    : '0';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Orders</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.orderStats.total_orders}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Completion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{orderCompletionRate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Manifests</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.manifestStats.total_manifests}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Processing Rate</p>
                <p className="text-2xl font-bold text-gray-900">{manifestProcessingRate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Order Status Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Order Status Distribution</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-yellow-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Pending</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.orderStats.pending_orders}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.orderStats.total_orders > 0 ? ((analytics.orderStats.pending_orders / analytics.orderStats.total_orders) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Completed</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.orderStats.completed_orders}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.orderStats.total_orders > 0 ? ((analytics.orderStats.completed_orders / analytics.orderStats.total_orders) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-red-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Cancelled</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.orderStats.cancelled_orders}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.orderStats.total_orders > 0 ? ((analytics.orderStats.cancelled_orders / analytics.orderStats.total_orders) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Manifest Status Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Manifest Status Distribution</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-yellow-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Pending</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.manifestStats.pending_manifests}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.manifestStats.total_manifests > 0 ? ((analytics.manifestStats.pending_manifests / analytics.manifestStats.total_manifests) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Approved</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.manifestStats.approved_manifests}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.manifestStats.total_manifests > 0 ? ((analytics.manifestStats.approved_manifests / analytics.manifestStats.total_manifests) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-red-400 rounded mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Rejected</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-bold text-gray-900 mr-2">
                    {analytics.manifestStats.rejected_manifests}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({analytics.manifestStats.total_manifests > 0 ? ((analytics.manifestStats.rejected_manifests / analytics.manifestStats.total_manifests) * 100).toFixed(1) : '0'}%)
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Orders Trend */}
        {analytics.orderStats.monthly_stats.length > 0 && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-medium text-gray-900">Monthly Orders Trend</h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.orderStats.monthly_stats.slice(-6).map((stat, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{stat.month}</span>
                    <div className="flex items-center">
                      <div 
                        className="bg-blue-200 h-2 rounded-full mr-3" 
                        style={{ 
                          width: `${Math.max(20, (stat.count / Math.max(...analytics.orderStats.monthly_stats.map(s => s.count))) * 120)}px` 
                        }}
                      ></div>
                      <span className="text-sm font-bold text-gray-900 w-8">{stat.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Daily Manifests Trend */}
        {analytics.manifestStats.daily_stats.length > 0 && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-medium text-gray-900">Daily Manifests Trend</h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.manifestStats.daily_stats.slice(-7).map((stat, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      {new Date(stat.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </span>
                    <div className="flex items-center">
                      <div 
                        className="bg-purple-200 h-2 rounded-full mr-3" 
                        style={{ 
                          width: `${Math.max(20, (stat.count / Math.max(...analytics.manifestStats.daily_stats.map(s => s.count))) * 120)}px` 
                        }}
                      ></div>
                      <span className="text-sm font-bold text-gray-900 w-8">{stat.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
