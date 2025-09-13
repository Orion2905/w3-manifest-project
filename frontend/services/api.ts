import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';

interface ApiError {
  message: string;
  status: number;
  details?: any;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const apiError: ApiError = {
          message: error.response?.data?.error || error.message || 'An error occurred',
          status: error.response?.status || 500,
          details: error.response?.data,
        };

        // Handle unauthorized requests
        if (error.response?.status === 401) {
          // Remove tokens and redirect to login
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }

        return Promise.reject(apiError);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // Upload file method
  async uploadFile<T>(url: string, file: File, additionalData?: Record<string, any>): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const response: AxiosResponse<T> = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  // POST request with FormData (for file uploads)
  async postFormData<T>(url: string, data: FormData): Promise<T> {
    const response = await this.client.post<T>(url, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // GET request for blob data (file downloads)
  async getBlob(url: string): Promise<Blob> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Set auth token
  setAuthToken(token: string) {
    Cookies.set('access_token', token, { expires: 7 }); // 7 days
  }

  // Remove auth token
  removeAuthToken() {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
  }

  // Get current token
  getAuthToken(): string | undefined {
    return Cookies.get('access_token');
  }
}

export const apiClient = new ApiClient();
export default apiClient;
