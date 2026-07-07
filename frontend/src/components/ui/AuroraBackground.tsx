export function AuroraBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-brand-600/30 blur-[100px]" />
      <div className="absolute -right-32 top-1/3 h-96 w-96 rounded-full bg-accent-500/20 blur-[100px]" />
      <div className="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-brand-400/20 blur-[100px]" />
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            'linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)',
          backgroundSize: '48px 48px',
        }}
      />
    </div>
  );
}
