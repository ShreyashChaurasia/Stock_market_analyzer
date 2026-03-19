import React from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onRetry }) => {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 p-3.5">
      <div className="flex items-start">
        <AlertCircle className="mt-0.5 h-4 w-4 text-red-600" />
        <div className="ml-3 flex-1">
          <h3 className="text-xs font-semibold uppercase tracking-[0.08em] text-red-800">Error</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm font-semibold text-red-600 hover:text-red-500"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
