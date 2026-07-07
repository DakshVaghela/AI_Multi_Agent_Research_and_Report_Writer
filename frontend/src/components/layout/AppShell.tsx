import { type ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { FileText, LayoutDashboard, LogOut, Plus } from 'lucide-react';
import { Logo } from '@/components/ui/Logo';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { useAuth } from '@/context/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/reports/new', label: 'New Report', icon: Plus },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="min-h-svh bg-surface-50 light:bg-slate-50">
      <div className="flex min-h-svh">
        <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 light:border-slate-200 bg-surface-0/60 light:bg-white px-5 py-6 md:flex">
          <Logo className="mb-10 px-1" />

          <nav className="flex flex-1 flex-col gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-500/10 text-brand-300 light:text-brand-700'
                      : 'text-slate-400 light:text-slate-500 hover:bg-white/5 light:hover:bg-slate-100 hover:text-slate-100 light:hover:text-slate-900'
                  }`
                }
              >
                <Icon className="h-4.5 w-4.5" />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto flex items-center gap-3 rounded-xl border border-white/5 light:border-slate-200 p-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-accent-500 text-sm font-semibold text-white">
              {user?.name?.[0]?.toUpperCase() ?? '?'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-100 light:text-slate-900">{user?.name}</p>
              <p className="truncate text-xs text-slate-500">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              aria-label="Log out"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-red-500/10 hover:text-red-400"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-white/5 light:border-slate-200 px-6 py-4 md:hidden">
            <Logo />
            <div className="flex items-center gap-2">
              <ThemeToggle />
            </div>
          </header>

          <header className="hidden items-center justify-between border-b border-white/5 light:border-slate-200 px-8 py-4 md:flex">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <FileText className="h-4 w-4" />
              <span>AI Multi-Agent Report Writer</span>
            </div>
            <ThemeToggle />
          </header>

          <main className="flex-1 overflow-y-auto px-5 py-6 md:px-8 md:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
