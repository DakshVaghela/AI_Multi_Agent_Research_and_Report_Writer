import { apiClient } from '@/api/client';
import type { JobStatusResponse } from '@/types/report';

export async function createReportJob(topic: string): Promise<JobStatusResponse> {
  const { data } = await apiClient.post<JobStatusResponse>('/reports', { topic });
  return data;
}

export async function getReportJob(jobId: string): Promise<JobStatusResponse> {
  const { data } = await apiClient.get<JobStatusResponse>(`/reports/${jobId}`);
  return data;
}

export function getReportPdfUrl(jobId: string): string {
  return `/api/reports/${jobId}/pdf`;
}
