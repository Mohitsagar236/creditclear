/**
 * Enhanced Notification System
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  X,
  Loader2 
} from 'lucide-react';

// Notification types and their configurations
const notificationConfig = {
  success: {
    icon: CheckCircle,
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
    iconColor: 'text-green-500',
    titleColor: 'text-green-800 dark:text-green-300',
    messageColor: 'text-green-700 dark:text-green-400'
  },
  error: {
    icon: AlertCircle,
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
    iconColor: 'text-red-500',
    titleColor: 'text-red-800 dark:text-red-300',
    messageColor: 'text-red-700 dark:text-red-400'
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    iconColor: 'text-yellow-500',
    titleColor: 'text-yellow-800 dark:text-yellow-300',
    messageColor: 'text-yellow-700 dark:text-yellow-400'
  },
  info: {
    icon: Info,
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    iconColor: 'text-blue-500',
    titleColor: 'text-blue-800 dark:text-blue-300',
    messageColor: 'text-blue-700 dark:text-blue-400'
  },
  loading: {
    icon: Loader2,
    bgColor: 'bg-gray-50 dark:bg-gray-800',
    borderColor: 'border-gray-200 dark:border-gray-700',
    iconColor: 'text-gray-500 animate-spin',
    titleColor: 'text-gray-800 dark:text-gray-300',
    messageColor: 'text-gray-700 dark:text-gray-400'
  }
};

// Individual Notification Component
export const Notification = ({
  type = 'info',
  title,
  message,
  onClose,
  closable = true,
  actions,
  className = ''
}) => {
  const config = notificationConfig[type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`
        relative p-4 rounded-lg border shadow-lg backdrop-blur-sm
        ${config.bgColor} ${config.borderColor}
        ${className}
      `}
    >
      <div className="flex items-start space-x-3">
        <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${config.iconColor}`} />
        
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className={`text-sm font-semibold ${config.titleColor}`}>
              {title}
            </h4>
          )}
          {message && (
            <p className={`text-sm ${title ? 'mt-1' : ''} ${config.messageColor}`}>
              {message}
            </p>
          )}
          
          {actions && (
            <div className="mt-3 flex space-x-2">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.onClick}
                  className={`
                    text-xs font-medium px-3 py-1 rounded-md transition-colors
                    ${action.variant === 'primary' 
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }
                  `}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
        
        {closable && onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

// Progress Notification
export const ProgressNotification = ({
  title,
  message,
  progress = 0,
  onClose,
  className = ''
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.9 }}
      className={`
        relative p-4 rounded-lg border shadow-lg backdrop-blur-sm
        bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800
        ${className}
      `}
    >
      <div className="flex items-start space-x-3">
        <Loader2 className="h-5 w-5 mt-0.5 flex-shrink-0 text-blue-500 animate-spin" />
        
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-300">
              {title}
            </h4>
          )}
          {message && (
            <p className="text-sm text-blue-700 dark:text-blue-400 mt-1">
              {message}
            </p>
          )}
          
          {progress > 0 && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-blue-600 dark:text-blue-400 mb-1">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                  className="bg-blue-600 h-2 rounded-full"
                />
              </div>
            </div>
          )}
        </div>
        
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

// Banner Notification (for important system-wide messages)
export const BannerNotification = ({
  type = 'info',
  title,
  message,
  onClose,
  onAction,
  actionLabel = 'Action',
  className = ''
}) => {
  const config = notificationConfig[type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className={`
        ${config.bgColor} ${config.borderColor} border-b px-4 py-3
        ${className}
      `}
    >
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-3">
          <Icon className={`h-5 w-5 ${config.iconColor}`} />
          <div>
            {title && (
              <span className={`font-medium ${config.titleColor}`}>
                {title}
              </span>
            )}
            {message && (
              <span className={`${title ? 'ml-2' : ''} ${config.messageColor}`}>
                {message}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {onAction && (
            <button
              onClick={onAction}
              className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              {actionLabel}
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Notification Container
export const NotificationContainer = ({ 
  notifications = [],
  position = 'top-right',
  className = '' 
}) => {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  };

  return (
    <div className={`fixed z-50 w-full max-w-sm ${positionClasses[position]} ${className}`}>
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            layout
            className="mb-3"
          >
            <Notification {...notification} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

// Toast Hook (simplified version for manual usage)
export const useNotifications = () => {
  const [notifications, setNotifications] = React.useState([]);

  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = { id, ...notification };
    
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove after duration (default 5 seconds)
    if (notification.duration !== 0) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration || 5000);
    }
    
    return id;
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success: (title, message, options = {}) => addNotification({ type: 'success', title, message, ...options }),
    error: (title, message, options = {}) => addNotification({ type: 'error', title, message, ...options }),
    warning: (title, message, options = {}) => addNotification({ type: 'warning', title, message, ...options }),
    info: (title, message, options = {}) => addNotification({ type: 'info', title, message, ...options }),
    loading: (title, message, options = {}) => addNotification({ type: 'loading', title, message, duration: 0, ...options })
  };
};

export default Notification;
