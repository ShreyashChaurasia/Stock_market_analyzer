import React from 'react';
import { TrendingUp, Activity, BarChart3, Home } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [currentPage, setCurrentPage] = React.useState<string>(
    window.location.pathname
  );

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Model Comparison', href: '/models', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                Stock Market Analyzer
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    onClick={(e) => {
                      e.preventDefault();
                      setCurrentPage(item.href);
                    }}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentPage === item.href
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                        : 'text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </a>
                );
              })}
              <div className="flex items-center space-x-2 pl-4 border-l border-gray-200 dark:border-gray-700">
                <Activity className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  API Online
                </span>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};