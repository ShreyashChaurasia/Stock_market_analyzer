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
    blue: 'bg-brand-accent/10 dark:bg-brand-accent/10 text-brand-accent dark:text-brand-accent',
    green: 'bg-financial-green/10 dark:bg-financial-green/10 text-financial-green dark:text-financial-green',
    red: 'bg-financial-red/10 dark:bg-financial-red/10 text-financial-red dark:text-financial-red',
    yellow: 'bg-financial-yellow/10 dark:bg-financial-yellow/10 text-financial-yellow dark:text-financial-yellow',
    purple: 'bg-purple-500/10 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400',
  };

  return (
    <div className="glass-panel p-6 group hover:translate-y-[-2px] transition-transform duration-300">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {title}
          </p>
          <p className="text-3xl font-mono font-bold text-gray-900 dark:text-white mt-2 tracking-tight">
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {subtitle}
            </p>
          )}
        </div>
        <div className={`p-4 rounded-xl transition-colors duration-300 ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
};