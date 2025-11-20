/**
 * Sync Service
 * T091: Frontend service for data synchronization
 */
import api from './api';

export interface SyncResponse {
  status: string;
  fetched_count: number;
  new_count: number;
  updated_count: number;
  message: string;
}

export interface SyncLog {
  id: number;
  sync_type: string;
  status: string;
  fetched_count: number;
  new_count: number;
  updated_count: number;
  error_message: string | null;
  created_at: string;
}

export interface SyncLogList {
  items: SyncLog[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Trigger manual data synchronization
 */
export async function fetchData(): Promise<SyncResponse> {
  const response = await api.post<SyncResponse>('/sync/fetch');
  return response.data;
}

/**
 * Get sync logs with pagination
 */
export async function getSyncLogs(params?: {
  page?: number;
  page_size?: number;
  sync_type?: string;
  status?: string;
}): Promise<SyncLogList> {
  const response = await api.get<SyncLogList>('/sync/logs', { params });
  return response.data;
}
