import { WifiOff } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export function OfflineIndicator() {
  const { t } = useTranslation();
  
  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-yellow-500 px-4 py-2 text-yellow-900"
      role="status"
      aria-live="polite"
    >
      <WifiOff className="h-4 w-4" />
      <span className="text-sm font-medium">
        {t('offline.title')} - {t('offline.message')}
      </span>
    </div>
  );
}
