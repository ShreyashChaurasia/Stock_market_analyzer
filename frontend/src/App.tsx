import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './pages/Dashboard';
import { ModelComparison } from './pages/ModelComparison';
import { useState, useEffect } from 'react';

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
      default:
        return <Dashboard />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      {renderPage()}
    </QueryClientProvider>
  );
}

export default App;