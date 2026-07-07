import type { ReactNode } from 'react';
import { Brain, FileCheck2, Search, Sparkles } from 'lucide-react';
import { Logo } from '@/components/ui/Logo';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { AuroraBackground } from '@/components/ui/AuroraBackground';

const features = [
  { icon: Search, text: 'Plans sub-questions and researches each one across the web' },
  { icon: Brain, text: 'Multi-agent pipeline: plan → research → write → critique' },
  { icon: FileCheck2, text: 'Iteratively revises drafts until the critic approves' },
];

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <div className="relative flex min-h-svh overflow-hidden bg-surface-0 light:bg-slate-50">
      <div className="absolute right-5 top-5 z-20">
        <ThemeToggle />
      </div>

      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-surface-0 via-surface-50 to-brand-900/40 p-12 lg:flex">
        <AuroraBackground />

        <div className="relative z-10">
          <Logo forceLight />
        </div>

        <div className="relative z-10 flex flex-1 items-center justify-center">
          <div className="relative h-72 w-72">
            <div className="absolute inset-0 animate-orbit rounded-full border border-dashed border-brand-400/30" />
            <div className="absolute inset-8 animate-orbit-reverse rounded-full border border-dashed border-accent-400/20" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-pulse-soft flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 shadow-2xl shadow-brand-500/40">
                <Sparkles className="h-10 w-10 text-white" />
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 space-y-4">
          <h2 className="font-display text-2xl font-semibold text-white">
            Research, written for you — <span className="text-gradient">by agents</span>
          </h2>
          <ul className="space-y-3">
            {features.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-slate-300">
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-accent-400" />
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex w-full flex-col items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-sm animate-slide-up">
          <div className="mb-8 lg:hidden">
            <Logo />
          </div>

          <h1 className="font-display text-2xl font-bold text-slate-900 dark:text-white">{title}</h1>
          <p className="mt-1.5 text-sm text-slate-500">{subtitle}</p>

          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  );
}
