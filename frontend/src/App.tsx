import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect, lazy, Suspense } from 'react';

const Dashboard = lazy(() =>
  import('./pages/Dashboard').then((module) => ({ default: module.Dashboard }))
);
const ModelComparison = lazy(() =>
  import('./pages/ModelComparison').then((module) => ({ default: module.ModelComparison }))
);
const NewsPage = lazy(() =>
  import('./pages/NewsPage').then((module) => ({ default: module.NewsPage }))
);
const HighConfidenceDashboard = lazy(() =>
  import('./pages/HighConfidenceDashboard').then((module) => ({ default: module.HighConfidenceDashboard }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.href.startsWith(window.location.origin)) {
        e.preventDefault();
        const path = new URL(link.href).pathname;
        window.history.pushState({}, '', path);
        setCurrentPath(path);
      }
    };

    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    document.addEventListener('click', handleClick);
    window.addEventListener('popstate', handlePopState);

    return () => {
      document.removeEventListener('click', handleClick);
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  const renderPage = () => {
    switch (currentPath) {
      case '/models':
        return <ModelComparison />;
      case '/news':
        return <NewsPage />;
      case '/quant-discovery':
      case '/high-confidence':
        return <HighConfidenceDashboard />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Suspense
        fallback={
          <div className="min-h-screen bg-[#f7f9fc] px-4 py-8 text-center text-sm font-semibold uppercase tracking-[0.12em] text-gray-500 dark:bg-brand-dark dark:text-gray-400">
            Loading dashboard module...
          </div>
        }
      >
        {renderPage()}
      </Suspense>
    </QueryClientProvider>
  );
}

export default App;