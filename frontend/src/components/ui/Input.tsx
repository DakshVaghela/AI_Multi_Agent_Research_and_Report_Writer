import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, id, className = '', ...rest }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={id} className="text-sm font-medium text-slate-300 light:text-slate-600">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <span className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">
              {icon}
            </span>
          )}
          <input
            ref={ref}
            id={id}
            className={`w-full rounded-xl border bg-surface-100 light:bg-white px-4 py-2.5 text-sm text-slate-100 light:text-slate-900 placeholder:text-slate-500 outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 ${
              icon ? 'pl-10' : ''
            } ${error ? 'border-red-500/50' : 'border-white/10 light:border-slate-200'} ${className}`}
            {...rest}
          />
        </div>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
    );
  },
);

Input.displayName = 'Input';
