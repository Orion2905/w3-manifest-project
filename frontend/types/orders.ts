export interface Order {
  id: number;
  service_id: string;
  external_service_id?: string;
  action: 'new' | 'change' | 'cancel';
  service_date: string;
  service_type: string;
  description: string;
  
  // Vehicle information
  vehicle_model?: string;
  vehicle_capacity?: string;
  
  // Passenger information
  passenger_count_adults: number;
  passenger_count_children: number;
  passenger_names: string[];
  
  // Contact information
  contact_phone?: string;
  contact_email?: string;
  
  // Location information
  pickup_location?: string;
  dropoff_location?: string;
  pickup_address?: string;
  dropoff_address?: string;
  pickup_time?: string;
  pickup_time_confirmed: boolean;
  
  // Flight information
  flight_number?: string;
  flight_departure_time?: string;
  flight_arrival_time?: string;
  
  // Additional details
  train_details?: string;
  operator_comments?: string;
  supplier_comments?: string;
  
  // Status and tracking
  status: 'pending' | 'approved' | 'processing' | 'completed' | 'cancelled' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  
  // Validation
  is_validated: boolean;
  validation_errors: string[];
  missing_data_flags: string[];
  
  // Relationships
  manifest_email_id?: number;
  created_by_user_id: number;
  approved_by_user_id?: number;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  approved_at?: string;
  processed_at?: string;
}

export interface OrderFilters {
  status?: string[];
  action?: string[];
  service_type?: string[];
  date_from?: string;
  date_to?: string;
  search?: string;
  priority?: string[];
  has_missing_data?: boolean;
  customer?: string;
}

export interface CreateOrderData {
  service_id: string;
  external_service_id?: string;
  action: 'new' | 'change' | 'cancel';
  service_date: string;
  service_type: string;
  description: string;
  
  // Vehicle information
  vehicle_model?: string;
  vehicle_capacity?: string;
  
  // Passenger information
  passenger_count_adults: number;
  passenger_count_children: number;
  passenger_names: string[];
  
  // Contact information
  contact_phone?: string;
  contact_email?: string;
  
  // Location information
  pickup_location?: string;
  dropoff_location?: string;
  pickup_address?: string;
  dropoff_address?: string;
  pickup_time?: string;
  pickup_time_confirmed?: boolean;
  
  // Flight information
  flight_number?: string;
  flight_departure_time?: string;
  flight_arrival_time?: string;
  
  // Additional details
  train_details?: string;
  operator_comments?: string;
  supplier_comments?: string;
  
  // Status and tracking
  status?: 'pending' | 'approved' | 'processing' | 'completed' | 'cancelled' | 'failed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
}

export interface UpdateOrderData {
  service_id?: string;
  external_service_id?: string;
  action?: 'new' | 'change' | 'cancel';
  service_date?: string;
  service_type?: string;
  description?: string;
  
  // Vehicle information
  vehicle_model?: string;
  vehicle_capacity?: string;
  
  // Passenger information
  passenger_count_adults?: number;
  passenger_count_children?: number;
  passenger_names?: string[];
  
  // Contact information
  contact_phone?: string;
  contact_email?: string;
  
  // Location information
  pickup_location?: string;
  dropoff_location?: string;
  pickup_address?: string;
  dropoff_address?: string;
  pickup_time?: string;
  pickup_time_confirmed?: boolean;
  
  // Flight information
  flight_number?: string;
  flight_departure_time?: string;
  flight_arrival_time?: string;
  
  // Additional details
  train_details?: string;
  operator_comments?: string;
  supplier_comments?: string;
  
  // Status and tracking
  status?: 'pending' | 'approved' | 'processing' | 'completed' | 'cancelled' | 'failed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
}

export interface OrdersResponse {
  orders: Order[];
  pagination: {
    page: number;
    pages: number;
    per_page: number;
    total: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface DashboardStats {
  total_orders: number;
  pending_orders: number;
  approved_orders: number;
  completed_orders: number;
  failed_orders: number;
  orders_with_missing_data: number;
  recent_activity: RecentActivity[];
  orders_by_type: { [key: string]: number };
  orders_by_status: { [key: string]: number };
  daily_orders: { date: string; count: number }[];
}

export interface RecentActivity {
  id: number;
  action: string;
  resource_type: string;
  resource_id: string;
  user_email: string;
  description: string;
  created_at: string;
}
