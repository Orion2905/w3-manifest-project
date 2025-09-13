import { apiClient } from './api';
import { Order, OrderFilters, CreateOrderData, UpdateOrderData } from '@/types/orders';
import { PaginatedResponse } from '@/types/api';

export const orderService = {
  // Get all orders with filters and pagination
  async getOrders(
    page: number = 1,
    limit: number = 20,
    filters?: OrderFilters
  ): Promise<PaginatedResponse<Order>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    if (filters) {
      if (filters.status) {
        if (Array.isArray(filters.status)) {
          filters.status.forEach(status => params.append('status', status));
        } else {
          params.append('status', filters.status);
        }
      }
      if (filters.customer) params.append('customer', filters.customer);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.search) params.append('search', filters.search);
    }

    return apiClient.get<PaginatedResponse<Order>>(`/orders?${params.toString()}`);
  },

  // Get order by ID
  async getOrder(id: string): Promise<Order> {
    return apiClient.get<Order>(`/orders/${id}`);
  },

  // Create new order
  async createOrder(data: CreateOrderData): Promise<Order> {
    return apiClient.post<Order>('/orders', data);
  },

  // Update order
  async updateOrder(id: string, data: UpdateOrderData): Promise<Order> {
    return apiClient.put<Order>(`/orders/${id}`, data);
  },

  // Delete order
  async deleteOrder(id: string): Promise<void> {
    return apiClient.delete(`/orders/${id}`);
  },

  // Get order statistics
  async getOrderStats(): Promise<{
    total_orders: number;
    pending_orders: number;
    completed_orders: number;
    cancelled_orders: number;
    monthly_stats: Array<{
      month: string;
      count: number;
    }>;
  }> {
    return apiClient.get('/orders/stats');
  },
};
