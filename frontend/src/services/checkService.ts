/**
 * Check Service
 * T092: Frontend service for check objects
 */
import api from './api';

export interface CheckObjectItem {
  id: number;
  check_item_name: string | null;
  check_method: string | null;
  standard_value: string | null;
  check_result: string | null;
  result_indicator: string | null;
}

export interface CheckObject {
  id: number;
  check_no: string;
  sample_name: string | null;
  company_name: string | null;
  status: number;
  sampling_time: string | null;
  check_result: string | null;
  report_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CheckObjectDetail extends CheckObject {
  sample_source: string | null;
  sample_base_num: string | null;
  product_date: string | null;
  specs: string | null;
  grade: string | null;
  executive_standards: string | null;
  production_license_num: string | null;
  sampling_num: string | null;
  sampling_site: string | null;
  sampling_address: string | null;
  commissioning_unit: string | null;
  is_subcontract: number;
  subcontract_lab: string | null;
  remark: string | null;
  check_items: CheckObjectItem[];
}

export interface CheckObjectList {
  items: CheckObject[];
  total: number;
  page: number;
  page_size: number;
}

export interface CheckObjectQuery {
  page?: number;
  page_size?: number;
  status?: number | null;
  company?: string;
  check_no?: string;
  start_date?: string;
  end_date?: string;
}

export interface CheckObjectUpdateData {
  sample_name?: string;
  company_name?: string;
  sample_source?: string;
  specs?: string;
  grade?: string;
  remark?: string;
  status?: number;
  check_items?: Array<{
    id?: number;
    check_item_name?: string;
    check_method?: string;
    standard_value?: string;
    check_result?: string;
    result_indicator?: string;
  }>;
}

/**
 * Get check objects with filters and pagination
 */
export async function getCheckObjects(query?: CheckObjectQuery): Promise<CheckObjectList> {
  const params: Record<string, any> = {};

  if (query) {
    if (query.page) params.page = query.page;
    if (query.page_size) params.page_size = query.page_size;
    if (query.status !== undefined && query.status !== null) params.status = query.status;
    if (query.company) params.company = query.company;
    if (query.check_no) params.check_no = query.check_no;
    if (query.start_date) params.start_date = query.start_date;
    if (query.end_date) params.end_date = query.end_date;
  }

  const response = await api.get<CheckObjectList>('/check-objects', { params });
  return response.data;
}

/**
 * Get check object detail by ID
 */
export async function getCheckObjectDetail(id: number): Promise<CheckObjectDetail> {
  const response = await api.get<CheckObjectDetail>(`/check-objects/${id}`);
  return response.data;
}

/**
 * Update check object
 */
export async function updateCheckObject(
  id: number,
  data: CheckObjectUpdateData
): Promise<CheckObjectDetail> {
  const response = await api.put<CheckObjectDetail>(`/check-objects/${id}`, data);
  return response.data;
}

/**
 * Save check result
 * T116: Save check result and update status
 */
export async function saveCheckResult(
  id: number,
  data: {
    check_result: string;
    check_items: Array<{
      id: number;
      check_result: string;
      result_indicator: string;
    }>;
  }
): Promise<CheckObjectDetail> {
  const response = await api.put<CheckObjectDetail>(`/check-objects/${id}/result`, data);
  return response.data;
}

/**
 * Upload report PDF
 * T117: Upload PDF report file
 */
export async function uploadReport(file: File): Promise<{ file_url: string; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<{ file_url: string; filename: string }>(
    '/reports/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
}

/**
 * Submit check result to client API
 * T131: Submit result to client system
 */
export async function submitResult(id: number): Promise<{ success: boolean; message: string }> {
  const response = await api.post<{ success: boolean; message: string }>(`/submit/${id}`);
  return response.data;
}

/**
 * Get status text
 */
export function getStatusText(status: number): string {
  switch (status) {
    case 0:
      return '待检测';
    case 1:
      return '已检测';
    case 2:
      return '已提交';
    default:
      return '未知';
  }
}

/**
 * Get status color for Ant Design
 */
export function getStatusColor(status: number): string {
  switch (status) {
    case 0:
      return 'warning';
    case 1:
      return 'processing';
    case 2:
      return 'success';
    default:
      return 'default';
  }
}

/**
 * Download PDF report by check_no
 * T151: Download PDF report
 */
export async function downloadReport(checkNo: string): Promise<Blob> {
  const response = await api.get(`/reports/download/${checkNo}`, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Export check results to Excel
 * T152: Export Excel with query filters
 */
export interface ExportExcelParams {
  check_object_ids?: number[];
  status?: number;
  company?: string;
  check_no?: string;
  start_date?: string;
  end_date?: string;
}

export async function exportExcel(params: ExportExcelParams): Promise<Blob> {
  const response = await api.post('/reports/export-excel', params, {
    responseType: 'blob',
  });
  return response.data;
}
