import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-brand-accent dark:bg-brand-accent/10 dark:text-brand-accent',
    green: 'bg-green-50 text-financial-green dark:bg-financial-green/10 dark:text-financial-green',
    red: 'bg-red-50 text-financial-red dark:bg-financial-red/10 dark:text-financial-red',
    yellow: 'bg-amber-50 text-financial-yellow dark:bg-financial-yellow/10 dark:text-financial-yellow',
    purple: 'bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400',
  };

  return (
    <div className="glass-panel p-4">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">
            {title}
          </p>
          <p className="mt-1.5 text-xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-2xl">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {subtitle}
            </p>
          )}
        </div>
        <div className={`rounded-md p-2.5 ${colorClasses[color]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
};
