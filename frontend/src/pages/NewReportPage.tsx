import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Sparkles, TriangleAlert } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/context/AuthContext';
import { createReportJob } from '@/api/reports';
import { addHistoryEntry } from '@/api/history';

const suggestions = [
  'The impact of quantum computing on modern cryptography',
  'Global adoption trends of electric vehicles in 2025',
  'How large language models are changing software engineering',
  'The economics of renewable energy storage',
];

export function NewReportPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [topic, setTopic] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!user || !topic.trim()) return;

    setError(null);
    setSubmitting(true);
    try {
      const job = await createReportJob(topic.trim());
      addHistoryEntry(user.id, {
        jobId: job.job_id,
        topic: job.topic,
        createdAt: new Date().toISOString(),
        status: job.status,
      });
      navigate(`/reports/${job.job_id}`);
    } catch {
      setError('Could not start the report job. Is the backend running on port 8000?');
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="mx-auto flex max-w-2xl flex-col items-center pt-8 text-center">
        <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 shadow-lg shadow-brand-500/30">
          <Sparkles className="h-6 w-6 text-white" />
        </div>
        <h1 className="font-display text-3xl font-bold text-slate-900 dark:text-white">
          What should we research today?
        </h1>
        <p className="mt-2 max-w-md text-sm text-slate-500">
          Give the agents a topic. They'll plan sub-questions, research the web, write a report, and
          critique it until it's ready.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 w-full">
          <div className="glass-panel flex flex-col gap-3 rounded-2xl p-3 sm:flex-row">
            <input
              autoFocus
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. The future of nuclear fusion energy"
              className="flex-1 rounded-xl bg-transparent px-3.5 py-3 text-sm text-slate-100 light:text-slate-900 placeholder:text-slate-500 outline-none"
              required
            />
            <Button type="submit" size="lg" loading={submitting} icon={<ArrowRight className="h-4 w-4" />}>
              Generate report
            </Button>
          </div>
        </form>

        {error && (
          <div className="mt-4 flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-3.5 py-2.5 text-sm text-red-400">
            <TriangleAlert className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <div className="mt-10 w-full">
          <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">Try an example</p>
          <div className="flex flex-wrap justify-center gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setTopic(s)}
                className="rounded-full border border-white/10 light:border-slate-200 bg-surface-100 light:bg-white px-3.5 py-1.5 text-xs text-slate-400 light:text-slate-600 transition-colors hover:border-brand-500/40 hover:text-brand-300"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
