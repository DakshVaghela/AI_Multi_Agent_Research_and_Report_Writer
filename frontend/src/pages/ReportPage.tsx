import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Download, ExternalLink, ListRestart, TriangleAlert } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { GeneratingLoader } from '@/components/ui/GeneratingLoader';
import { useReportJob } from '@/hooks/useReportJob';
import { getReportPdfUrl } from '@/api/reports';
import { updateHistoryStatus } from '@/api/history';
import { useAuth } from '@/context/AuthContext';

export function ReportPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const { user } = useAuth();
  const { job, error } = useReportJob(jobId);

  useEffect(() => {
    if (user && job) {
      updateHistoryStatus(user.id, job.job_id, job.status);
    }
  }, [user, job]);

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl">
        {!job && !error && (
          <div className="glass-panel rounded-2xl">
            <GeneratingLoader topic="…" />
          </div>
        )}

        {job && (job.status === 'pending' || job.status === 'running') && (
          <div className="glass-panel rounded-2xl">
            <GeneratingLoader topic={job.topic} />
          </div>
        )}

        {job?.status === 'failed' && (
          <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-14 text-center">
            <TriangleAlert className="h-10 w-10 text-red-400" />
            <div>
              <h2 className="font-display text-lg font-semibold text-slate-900 dark:text-white">
                Report generation failed
              </h2>
              <p className="mt-1 max-w-md text-sm text-slate-500">
                {job.error ?? 'Something went wrong while generating this report.'}
              </p>
            </div>
            <Link to="/reports/new">
              <Button variant="secondary" icon={<ListRestart className="h-4 w-4" />}>
                Try another topic
              </Button>
            </Link>
          </div>
        )}

        {job?.status === 'completed' && job.report && (
          <article className="animate-fade-in">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <StatusBadge status={job.status} />
              <div className="flex gap-2">
                <a href={getReportPdfUrl(job.job_id)} target="_blank" rel="noreferrer">
                  <Button variant="secondary" size="sm" icon={<ExternalLink className="h-4 w-4" />}>
                    Open PDF
                  </Button>
                </a>
                <a href={getReportPdfUrl(job.job_id)} download={`${job.topic}.pdf`}>
                  <Button size="sm" icon={<Download className="h-4 w-4" />}>
                    Download PDF
                  </Button>
                </a>
              </div>
            </div>

            <h1 className="font-display text-3xl font-bold text-slate-900 dark:text-white">
              {job.report.title}
            </h1>
            <p className="mt-2 text-sm text-slate-500">Topic: {job.topic}</p>

            <div className="prose prose-slate dark:prose-invert prose-headings:font-display prose-a:text-brand-400 mt-8 max-w-none">
              <h2>Executive summary</h2>
              <p>{job.report.executive_summary}</p>

              <h2>Introduction</h2>
              <p>{job.report.introduction}</p>

              <ReactMarkdown>{job.report.main_content}</ReactMarkdown>

              <h2>Conclusion</h2>
              <p>{job.report.conclusion}</p>

              {job.report.references.length > 0 && (
                <>
                  <h2>References</h2>
                  <ol>
                    {job.report.references.map((ref) => (
                      <li key={ref.url}>
                        <a href={ref.url} target="_blank" rel="noreferrer">
                          {ref.title || ref.url}
                        </a>
                        <span className="text-slate-500"> — {ref.source}</span>
                      </li>
                    ))}
                  </ol>
                </>
              )}
            </div>
          </article>
        )}

        {error && !job && (
          <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-14 text-center">
            <TriangleAlert className="h-10 w-10 text-amber-400" />
            <p className="text-sm text-slate-500">{error}</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
