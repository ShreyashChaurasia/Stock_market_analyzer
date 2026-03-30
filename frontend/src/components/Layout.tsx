import React from 'react';
import { TrendingUp, BarChart3, Home, Github, Newspaper, Radar } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const GITHUB_REPO_URL = 'https://github.com/ShreyashChaurasia/Stock_market_analyzer';
  const [currentPage, setCurrentPage] = React.useState<string>(
    window.location.pathname
  );

  React.useEffect(() => {
    const handlePopState = () => setCurrentPage(window.location.pathname);
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Model Comparison', href: '/models', icon: BarChart3 },
    { name: 'News', href: '/news', icon: Newspaper },
    { name: 'Quant Discovery', href: '/quant-discovery', icon: Radar },
  ];

  return (
    <div className="min-h-screen bg-[#f7f9fc] dark:bg-brand-dark transition-colors font-sans text-gray-900 dark:text-gray-100">
      <nav className="sticky top-0 z-50 border-b border-gray-200/80 bg-white/95 backdrop-blur-sm dark:border-gray-800 dark:bg-brand-dark/95 transition-colors">
        <div className="mx-auto w-full max-w-[1360px] px-3 sm:px-5 lg:px-6">
          <div className="flex h-14 items-center justify-between">
            <div className="flex items-center">
              <div className="mr-2.5 flex items-center justify-center rounded-md bg-blue-50 p-1.5 text-blue-600 dark:bg-brand-accent/10 dark:text-brand-accent">
                <TrendingUp className="h-4 w-4" />
              </div>
              <span className="text-base font-semibold text-gray-900 dark:text-white tracking-tight sm:text-lg">
                Stock Market <span className="text-blue-600 dark:text-brand-accent">Analyzer</span>
              </span>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4">
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-semibold text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-brand-surfaceHover dark:hover:text-gray-100 sm:text-sm"
                aria-label="View project on GitHub"
              >
                <Github className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">GitHub</span>
              </a>
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive =
                  currentPage === item.href
                  || (item.href === '/quant-discovery' && currentPage === '/high-confidence');
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    onClick={(e) => {
                      e.preventDefault();
                      setCurrentPage(item.href);
                    }}
                    className={`flex items-center space-x-1.5 rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors sm:text-sm ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 dark:bg-white/5 dark:text-brand-accent'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-brand-surfaceHover dark:hover:text-gray-100'
                    }`}
                  >
                    <Icon className={`h-3.5 w-3.5 ${isActive ? 'opacity-100' : 'opacity-75'}`} />
                    <span className="hidden sm:inline">{item.name}</span>
                  </a>
                );
              })}
              <div className="ml-1 hidden items-center space-x-2 border-l border-gray-200 pl-3 dark:border-gray-700 lg:flex">
                <div className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-financial-green opacity-70"></span>
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-financial-green"></span>
                </div>
                <span className="text-xs font-medium uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                  System Online
                </span>
              </div>
              <div className="pl-1 sm:pl-2">
                <ThemeToggle />
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="mx-auto w-full max-w-[1360px] px-3 py-4 sm:px-5 lg:px-6 lg:py-5">
        {children}
      </main>
    </div>
  );
};
