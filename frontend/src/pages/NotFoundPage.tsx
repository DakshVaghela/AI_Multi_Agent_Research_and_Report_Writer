import { Link } from 'react-router-dom';
import { Compass } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { AuroraBackground } from '@/components/ui/AuroraBackground';

export function NotFoundPage() {
  return (
    <div className="relative flex min-h-svh flex-col items-center justify-center overflow-hidden bg-surface-0 light:bg-slate-50 px-6 text-center">
      <AuroraBackground />
      <Compass className="relative z-10 h-10 w-10 text-brand-400" />
      <h1 className="relative z-10 mt-4 font-display text-4xl font-bold text-white">404</h1>
      <p className="relative z-10 mt-2 text-sm text-slate-400">This page doesn't exist.</p>
      <Link to="/" className="relative z-10 mt-6">
        <Button>Back home</Button>
      </Link>
    </div>
  );
}
