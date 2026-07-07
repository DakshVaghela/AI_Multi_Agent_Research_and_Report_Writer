import type { JobStatus, ReportHistoryEntry } from '@/types/report';

const HISTORY_KEY_PREFIX = 'nexus_history_';

function key(userId: string): string {
  return `${HISTORY_KEY_PREFIX}${userId}`;
}

export function getHistory(userId: string): ReportHistoryEntry[] {
  try {
    const raw = JSON.parse(localStorage.getItem(key(userId)) ?? '[]') as ReportHistoryEntry[];
    return raw.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  } catch {
    return [];
  }
}

export function addHistoryEntry(userId: string, entry: ReportHistoryEntry): void {
  const history = getHistory(userId);
  localStorage.setItem(key(userId), JSON.stringify([entry, ...history]));
}

export function updateHistoryStatus(userId: string, jobId: string, status: JobStatus): void {
  const history = getHistory(userId).map((entry) =>
    entry.jobId === jobId ? { ...entry, status } : entry,
  );
  localStorage.setItem(key(userId), JSON.stringify(history));
}
