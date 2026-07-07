import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileStack, FileText, Globe2, History, Plus, RefreshCw, Sparkles } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { useAuth } from '@/context/AuthContext';
import { getHistory, updateHistoryStatus } from '@/api/history';
import { getReportJob } from '@/api/reports';
import type { ReportHistoryEntry } from '@/types/report';

const features = [
  {
    icon: Globe2,
    title: 'Multi-source research',
    description: 'Fans each sub-question out across web search providers and dedupes results.',
  },
  {
    icon: FileStack,
    title: 'Structured reports',
    description: 'Executive summary, introduction, sections, conclusion, and citations — every time.',
  },
  {
    icon: RefreshCw,
    title: 'Self-critiquing agent',
    description: 'A critic agent reviews each draft and sends it back for revision until it is approved.',
  },
];

export function DashboardPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<ReportHistoryEntry[]>([]);

  useEffect(() => {
    if (!user) return;
    const entries = getHistory(user.id);
    setHistory(entries);

    const pending = entries.filter((e) => e.status === 'pending' || e.status === 'running');
    if (pending.length === 0) return;

    Promise.all(
      pending.map(async (entry) => {
        try {
          const job = await getReportJob(entry.jobId);
          if (job.status !== entry.status) {
            updateHistoryStatus(user.id, entry.jobId, job.status);
          }
          return { ...entry, status: job.status };
        } catch {
          return entry;
        }
      }),
    ).then((updated) => {
      setHistory((prev) => prev.map((e) => updated.find((u) => u.jobId === e.jobId) ?? e));
    });
  }, [user]);

  const completedCount = history.filter((h) => h.status === 'completed').length;
  const inProgressCount = history.filter((h) => h.status === 'pending' || h.status === 'running').length;

  return (
    <AppShell>
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="font-display text-2xl font-bold text-slate-900 dark:text-white">
              Welcome back, {user?.name?.split(' ')[0]}
            </h1>
            <p className="mt-1 text-sm text-slate-500">Here's what's happening with your research reports.</p>
          </div>
          <Link to="/reports/new">
            <Button size="lg" icon={<Plus className="h-4 w-4" />}>
              New report
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatTile icon={FileText} label="Total reports" value={history.length} />
          <StatTile icon={Sparkles} label="Completed" value={completedCount} />
          <StatTile icon={RefreshCw} label="In progress" value={inProgressCount} />
        </div>

        <div>
          <h2 className="mb-4 font-display text-lg font-semibold text-slate-900 dark:text-white">
            What Nexus Research does
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="glass-panel rounded-2xl p-5 transition-transform hover:-translate-y-0.5"
              >
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/20 to-accent-500/20 text-brand-300">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="font-medium text-slate-900 dark:text-white">{title}</h3>
                <p className="mt-1 text-sm text-slate-500">{description}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-4 flex items-center gap-2">
            <History className="h-4 w-4 text-slate-500" />
            <h2 className="font-display text-lg font-semibold text-slate-900 dark:text-white">Recent reports</h2>
          </div>

          {history.length === 0 ? (
            <div className="glass-panel flex flex-col items-center gap-3 rounded-2xl p-12 text-center">
              <FileText className="h-8 w-8 text-slate-600" />
              <p className="text-sm text-slate-500">You haven't generated any reports yet.</p>
              <Link to="/reports/new">
                <Button variant="secondary" size="sm" icon={<Plus className="h-4 w-4" />}>
                  Generate your first report
                </Button>
              </Link>
            </div>
          ) : (
            <div className="glass-panel divide-y divide-white/5 light:divide-slate-200 overflow-hidden rounded-2xl">
              {history.map((entry) => (
                <Link
                  key={entry.jobId}
                  to={`/reports/${entry.jobId}`}
                  className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-white/5 light:hover:bg-slate-50"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-900 dark:text-white">{entry.topic}</p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {new Date(entry.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <StatusBadge status={entry.status} />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function StatTile({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof FileText;
  label: string;
  value: number;
}) {
  return (
    <div className="glass-panel flex items-center gap-4 rounded-2xl p-5">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/20 to-accent-500/20 text-brand-300">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="font-display text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </div>
  );
}
