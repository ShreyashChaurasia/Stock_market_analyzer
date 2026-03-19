import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Loading...' }) => {
  return (
    <div className="glass-panel flex flex-col items-center justify-center py-8">
      <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary-600"></div>
      <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  );
};
