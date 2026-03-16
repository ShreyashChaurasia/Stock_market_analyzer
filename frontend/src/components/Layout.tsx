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
    <div className="min-h-screen bg-gray-50 dark:bg-brand-dark transition-colors font-sans text-gray-900 dark:text-gray-100">
      <nav className="sticky top-0 z-50 bg-white dark:bg-brand-dark border-b border-gray-200 dark:border-white/5 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center justify-center p-2 rounded-lg bg-blue-50 dark:bg-brand-accent/10 text-blue-600 dark:text-brand-accent mr-3">
                <TrendingUp className="h-6 w-6" />
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                Stock Market <span className="text-blue-600 dark:text-brand-accent">Analyzer</span>
              </span>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = currentPage === item.href;
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    onClick={(e) => {
                      e.preventDefault();
                      setCurrentPage(item.href);
                    }}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 dark:bg-white/5 text-blue-700 dark:text-brand-accent'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-brand-surfaceHover hover:text-gray-900 dark:hover:text-gray-100'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? 'opacity-100' : 'opacity-70'}`} />
                    <span className="hidden sm:inline">{item.name}</span>
                  </a>
                );
              })}
              <div className="hidden sm:flex items-center space-x-2 pl-4 ml-2 border-l border-gray-200 dark:border-gray-700">
                <div className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-financial-green opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-financial-green"></span>
                </div>
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  System Online
                </span>
              </div>
              <div className="pl-2 sm:pl-4">
                <ThemeToggle />
              </div>
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