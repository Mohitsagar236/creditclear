/**
 * Enhanced Loading Components with Multiple Variants
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Loader, RefreshCw } from 'lucide-react';

// Skeleton loader for cards
export const SkeletonCard = ({ className = "" }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 animate-pulse ${className}`}>
    <div className="flex items-center justify-between mb-4">
      <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/3"></div>
      <div className="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
    </div>
    <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
  </div>
);

// Chart skeleton
export const SkeletonChart = ({ className = "" }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 animate-pulse ${className}`}>
    <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/3 mb-6"></div>
    <div className="h-64 bg-gray-300 dark:bg-gray-600 rounded"></div>
  </div>
);

// Spinner variants
export const SpinnerDots = () => (
  <div className="flex space-x-1">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-2 h-2 bg-blue-600 rounded-full"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [1, 0.5, 1],
        }}
        transition={{
          duration: 0.6,
          repeat: Infinity,
          delay: i * 0.2,
        }}
      />
    ))}
  </div>
);

export const SpinnerBars = () => (
  <div className="flex space-x-1">
    {[0, 1, 2, 3, 4].map((i) => (
      <motion.div
        key={i}
        className="w-1 h-8 bg-blue-600 rounded-full"
        animate={{
          scaleY: [1, 2, 1],
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          delay: i * 0.1,
        }}
      />
    ))}
  </div>
);

export const SpinnerPulse = () => (
  <motion.div
    className="w-16 h-16 bg-blue-600 rounded-full"
    animate={{
      scale: [1, 1.2, 1],
      opacity: [1, 0.5, 1],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
    }}
  />
);

// Full page loading
export const PageLoader = ({ message = "Loading..." }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"
      />
      <p className="text-gray-600 dark:text-gray-300 font-medium">{message}</p>
    </motion.div>
  </div>
);

// Button loading states
export const ButtonSpinner = ({ size = "sm" }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6"
  };

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className={`border-2 border-current border-t-transparent rounded-full ${sizeClasses[size]}`}
    />
  );
};

// Data loading placeholder
export const DataPlaceholder = ({ icon: Icon = Activity, title = "Loading data...", description }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex flex-col items-center justify-center p-12 text-center"
  >
    <motion.div
      animate={{ scale: [1, 1.1, 1] }}
      transition={{ duration: 2, repeat: Infinity }}
      className="p-4 bg-blue-100 dark:bg-blue-900 rounded-full mb-4"
    >
      <Icon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
    </motion.div>
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
    {description && (
      <p className="text-gray-600 dark:text-gray-400 max-w-sm">{description}</p>
    )}
  </motion.div>
);

export default PageLoader;
