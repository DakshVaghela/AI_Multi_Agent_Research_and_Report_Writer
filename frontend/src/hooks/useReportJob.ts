import { useEffect, useRef, useState } from 'react';
import { isAxiosError } from 'axios';
import { getReportJob } from '@/api/reports';
import type { JobStatusResponse } from '@/types/report';

const POLL_INTERVAL_MS = 2500;

export function useReportJob(jobId: string | undefined) {
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;

    async function poll() {
      try {
        const data = await getReportJob(jobId!);
        if (cancelled) return;
        setJob(data);
        setError(null);

        if (data.status === 'pending' || data.status === 'running') {
          timeoutRef.current = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (cancelled) return;

        if (isAxiosError(err) && err.response?.status === 404) {
          setError('This report no longer exists — the server may have restarted before it finished.');
          return;
        }

        setError('Unable to reach the report service. Retrying…');
        timeoutRef.current = setTimeout(poll, POLL_INTERVAL_MS);
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [jobId]);

  return { job, error };
}
