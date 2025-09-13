import { apiClient } from './api';
import { Manifest, ManifestEmail, ParseManifestResponse } from '@/types/manifest';
import { PaginatedResponse } from '@/types/api';

export const manifestService = {
  // Parse manifest file
  async parseManifest(file: File): Promise<ParseManifestResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.postFormData<ParseManifestResponse>('/manifest/parse', formData);
  },

  // Get all manifest emails
  async getManifestEmails(
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<ManifestEmail>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    return apiClient.get<PaginatedResponse<ManifestEmail>>(`/manifest/emails?${params.toString()}`);
  },

  // Get manifest email by ID
  async getManifestEmail(id: number): Promise<ManifestEmail> {
    return apiClient.get<ManifestEmail>(`/manifest/emails/${id}`);
  },

  // Get manifest by ID
  async getManifest(id: number): Promise<Manifest> {
    return apiClient.get<Manifest>(`/manifest/${id}`);
  },

  // Approve manifest
  async approveManifest(id: number): Promise<Manifest> {
    return apiClient.post<Manifest>(`/manifest/${id}/approve`);
  },

  // Reject manifest
  async rejectManifest(id: number, reason: string): Promise<Manifest> {
    return apiClient.post<Manifest>(`/manifest/${id}/reject`, { reason });
  },

  // Download manifest file
  async downloadManifest(id: number): Promise<Blob> {
    return apiClient.getBlob(`/manifest/${id}/download`);
  },

  // Upload manifest via email processing
  async uploadManifest(file: File, subject?: string, sender?: string): Promise<ManifestEmail> {
    const formData = new FormData();
    formData.append('file', file);
    if (subject) formData.append('subject', subject);
    if (sender) formData.append('sender', sender);
    
    return apiClient.postFormData<ManifestEmail>('/manifest/upload', formData);
  },

  // Get manifest processing statistics
  async getManifestStats(): Promise<{
    total_manifests: number;
    pending_manifests: number;
    approved_manifests: number;
    rejected_manifests: number;
    daily_stats: Array<{
      date: string;
      count: number;
    }>;
  }> {
    return apiClient.get('/manifest/stats');
  },
};
