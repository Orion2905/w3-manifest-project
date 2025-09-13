export interface ManifestEmail {
  id: number;
  subject: string;
  sender: string;
  received_at: string;
  processed_at?: string;
  status: 'pending' | 'processing' | 'processed' | 'failed';
  services_found: number;
  orders_created: number;
  original_filename: string;
  processing_errors: string[];
  processed_by?: string;
}

export interface Manifest {
  id: number;
  subject: string;
  sender: string;
  body: string;
  filename: string;
  file_content: string;
  received_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_services: number;
  parsed_services: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export interface ParseManifestResponse {
  manifest: Manifest;
  services: ParsedService[];
  total_services: number;
  valid_services: number;
  invalid_services: number;
  errors: string[];
}

export interface ManifestUploadResponse {
  message: string;
  manifest_id: number;
  services_found: number;
  orders_created: number;
  created_orders: Partial<Order>[];
  errors: string[];
  parser_warnings: string[];
}

export interface ManifestHistory {
  manifests: ManifestEmail[];
  pagination: {
    page: number;
    pages: number;
    per_page: number;
    total: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface ParsedService {
  action: string;
  service_id: string;
  service_date: string | null;
  service_type: string;
  description: string;
  vehicle_model: string;
  vehicle_capacity: string;
  passenger_count_adults: number;
  passenger_count_children: number;
  passenger_names: string[];
  contact_phone: string;
  pickup_location: string;
  pickup_time: string;
  flight_number: string;
  missing_data_flags: string[];
}

import { Order } from './orders';
