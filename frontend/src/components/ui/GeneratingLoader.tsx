import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, FileEdit, ScanSearch, Sparkles, Telescope } from 'lucide-react';

const stages = [
  { icon: Telescope, label: 'Planning sub-questions', detail: 'Breaking your topic down into researchable angles' },
  { icon: ScanSearch, label: 'Researching the web', detail: 'Searching, extracting, and summarizing sources' },
  { icon: FileEdit, label: 'Writing the draft', detail: 'Turning research notes into a structured report' },
  { icon: Brain, label: 'Critiquing & revising', detail: 'A critic agent reviews the draft for gaps and clarity' },
];

const STAGE_DURATION_MS = 7000;

export function GeneratingLoader({ topic }: { topic: string }) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, stages.length - 1));
    }, STAGE_DURATION_MS);
    return () => clearInterval(interval);
  }, []);

  const Stage = stages[stageIndex];

  return (
    <div className="flex flex-col items-center px-6 py-16 text-center">
      <div className="relative mb-10 h-32 w-32">
        <div className="absolute inset-0 animate-orbit rounded-full border-2 border-dashed border-brand-400/30" />
        <div className="absolute inset-5 animate-orbit-reverse rounded-full border-2 border-dashed border-accent-400/30" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-pulse-soft flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 shadow-xl shadow-brand-500/30">
            <Sparkles className="h-7 w-7 text-white" />
          </div>
        </div>
      </div>

      <p className="max-w-md text-sm text-slate-500">
        Generating a report on <span className="font-medium text-slate-300 light:text-slate-700">"{topic}"</span>
      </p>

      <div className="relative mt-8 h-16 w-full max-w-xs">
        <AnimatePresence mode="wait">
          <motion.div
            key={stageIndex}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35 }}
            className="absolute inset-0 flex flex-col items-center gap-1"
          >
            <div className="flex items-center gap-2 font-display text-base font-semibold text-slate-900 dark:text-white">
              <Stage.icon className="h-4.5 w-4.5 text-brand-400" />
              {Stage.label}
            </div>
            <p className="text-xs text-slate-500">{Stage.detail}</p>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="mt-6 flex gap-2">
        {stages.map((s, i) => (
          <div
            key={s.label}
            className={`h-1.5 w-8 rounded-full transition-colors duration-500 ${
              i <= stageIndex ? 'bg-gradient-to-r from-brand-500 to-accent-500' : 'bg-surface-300'
            }`}
          />
        ))}
      </div>

      <p className="mt-8 text-xs text-slate-600">
        This can take a few minutes — agents are researching real sources before writing.
      </p>
    </div>
  );
}
