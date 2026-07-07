export interface Citation {
  title: string;
  url: string;
  source: string;
  snippet: string;
  retrieved_at: string;
}

export interface Report {
  title: string;
  executive_summary: string;
  introduction: string;
  main_content: string;
  conclusion: string;
  references: Citation[];
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  topic: string;
  error: string | null;
  report: Report | null;
}

export interface ReportHistoryEntry {
  jobId: string;
  topic: string;
  createdAt: string;
  status: JobStatus;
}
