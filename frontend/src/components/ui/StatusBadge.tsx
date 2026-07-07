import { CheckCircle2, CircleDashed, Loader2, XCircle } from 'lucide-react';
import type { JobStatus } from '@/types/report';

const config: Record<JobStatus, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  pending: { label: 'Queued', className: 'bg-slate-500/10 text-slate-400 border-slate-500/20', icon: CircleDashed },
  running: { label: 'Generating', className: 'bg-brand-500/10 text-brand-300 border-brand-500/20', icon: Loader2 },
  completed: { label: 'Completed', className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', icon: CheckCircle2 },
  failed: { label: 'Failed', className: 'bg-red-500/10 text-red-400 border-red-500/20', icon: XCircle },
};

export function StatusBadge({ status }: { status: JobStatus }) {
  const { label, className, icon: Icon } = config[status];

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${className}`}>
      <Icon className={`h-3 w-3 ${status === 'running' ? 'animate-spin' : ''}`} />
      {label}
    </span>
  );
}
