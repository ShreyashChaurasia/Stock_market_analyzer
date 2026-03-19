import React, { useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

export const ThemeToggle: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useThemeStore();

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <button
      onClick={toggleDarkMode}
      className="rounded-md border border-gray-200 bg-gray-100 p-1.5 transition-colors hover:bg-gray-200 dark:border-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600"
      aria-label="Toggle dark mode"
    >
      {isDarkMode ? (
        <Sun className="h-4 w-4 text-yellow-500" />
      ) : (
        <Moon className="h-4 w-4 text-gray-700" />
      )}
    </button>
  );
};
