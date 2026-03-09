import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { useEffect, useState } from 'react';

interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  onClose: () => void;
  duration?: number;
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const styles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const iconStyles = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

export function Toast({ type, title, message, onClose, duration = 5000 }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false);
  const Icon = icons[type];
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(onClose, 300);
    }, duration);
    
    return () => clearTimeout(timer);
  }, [duration, onClose]);
  
  const handleClose = () => {
    setIsExiting(true);
    setTimeout(onClose, 300);
  };
  
  return (
    <div
      className={clsx(
        'flex w-full max-w-sm items-start gap-3 rounded-lg border p-4 shadow-lg',
        'animate-slide-up',
        styles[type],
        isExiting && 'animate-fade-out'
      )}
      role="alert"
    >
      <Icon className={clsx('h-5 w-5 flex-shrink-0', iconStyles[type])} />
      
      <div className="flex-1">
        {title && (
          <p className="font-medium">{title}</p>
        )}
        <p className={clsx(title && 'text-sm opacity-90')}>{message}</p>
      </div>
      
      <button
        onClick={handleClose}
        className="flex-shrink-0 rounded p1 hover:bg-black/5"
        aria-label="Close"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
