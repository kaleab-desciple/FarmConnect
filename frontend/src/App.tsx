import { Router } from './app/router';
import { useEffect } from 'react';
import { useUIStore } from './app/store/useUIStore';
import { useAuthStore } from './app/store/useAuthStore';
import { Toast } from './shared/components/ui/Toast';
import { OfflineIndicator } from './shared/components/layout/OfflineIndicator';

function App() {
  const { theme, isOffline, notifications, removeNotification } = useUIStore();
  const { isAuthenticated } = useAuthStore();
  
  // Apply theme
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('dark', 'high-contrast');
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'high-contrast') {
      root.classList.add('high-contrast');
    }
  }, [theme]);
  
  // Track online/offline status
  useEffect(() => {
    const handleOnline = () => useUIStore.getState().setOffline(false);
    const handleOffline = () => useUIStore.getState().setOffline(true);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Initial check
    if (!navigator.onLine) {
      useUIStore.getState().setOffline(true);
    }
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  // Track user activity for session management
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const handleActivity = () => {
      useAuthStore.getState().updateLastActivity();
    };
    
    window.addEventListener('click', handleActivity);
    window.addEventListener('keypress', handleActivity);
    
    return () => {
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('keypress', handleActivity);
    };
  }, [isAuthenticated]);
  
  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      {/* Offline indicator banner */}
      {isOffline && <OfflineIndicator />}
      
      {/* Main router */}
      <Router />
      
      {/* Toast notifications */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {notifications.map((notification) => (
          <Toast
            key={notification.id}
            type={notification.type}
            title={notification.title}
            message={notification.message}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
