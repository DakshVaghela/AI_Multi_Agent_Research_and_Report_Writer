export function LogoMark({ className = 'h-9 w-9' }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center rounded-xl bg-surface-0 ${className}`}>
      <svg viewBox="0 0 64 64" className="h-2/3 w-2/3">
        <defs>
          <linearGradient id="logo-grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#818cf8" />
            <stop offset="100%" stopColor="#22d3ee" />
          </linearGradient>
        </defs>
        <circle cx="32" cy="32" r="20" fill="none" stroke="url(#logo-grad)" strokeWidth="4" />
        <circle cx="32" cy="16" r="4" fill="url(#logo-grad)" />
        <circle cx="47" cy="40" r="4" fill="url(#logo-grad)" />
        <circle cx="17" cy="40" r="4" fill="url(#logo-grad)" />
        <circle cx="32" cy="32" r="5" fill="url(#logo-grad)" />
      </svg>
    </div>
  );
}

export function Logo({ className = '', forceLight = false }: { className?: string; forceLight?: boolean }) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <LogoMark />
      <span
        className={`font-display text-lg font-semibold tracking-tight ${
          forceLight ? 'text-white' : 'text-slate-900 dark:text-white'
        }`}
      >
        Nexus <span className="text-gradient">Research</span>
      </span>
    </div>
  );
}
