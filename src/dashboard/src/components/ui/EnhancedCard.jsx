/**
 * Enhanced Card Components with Modern UI/UX
 */
import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, MoreVertical, Eye, Settings } from 'lucide-react';

// Enhanced Metric Card
export const EnhancedMetricCard = ({
  title,
  value,
  trend,
  trendValue,
  icon: Icon,
  color = "blue",
  format = "number",
  className = "",
  onClick,
  ...props
}) => {
  const formatValue = (val) => {
    if (format === "percentage") return `${val}%`;
    if (format === "currency") return `$${val.toLocaleString()}`;
    if (format === "number") return val.toLocaleString();
    return val;
  };

  const colorClasses = {
    blue: {
      bg: "from-blue-500 to-blue-600",
      text: "text-blue-600",
      light: "bg-blue-50 dark:bg-blue-900/20",
      ring: "ring-blue-500/20"
    },
    green: {
      bg: "from-green-500 to-green-600", 
      text: "text-green-600",
      light: "bg-green-50 dark:bg-green-900/20",
      ring: "ring-green-500/20"
    },
    purple: {
      bg: "from-purple-500 to-purple-600",
      text: "text-purple-600", 
      light: "bg-purple-50 dark:bg-purple-900/20",
      ring: "ring-purple-500/20"
    },
    orange: {
      bg: "from-orange-500 to-orange-600",
      text: "text-orange-600",
      light: "bg-orange-50 dark:bg-orange-900/20", 
      ring: "ring-orange-500/20"
    },
    red: {
      bg: "from-red-500 to-red-600",
      text: "text-red-600",
      light: "bg-red-50 dark:bg-red-900/20",
      ring: "ring-red-500/20"
    }
  };

  const colors = colorClasses[color];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer group ${className}`}
      {...props}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-2xl ${colors.light} group-hover:scale-110 transition-transform duration-300`}>
          <Icon className={`h-6 w-6 ${colors.text}`} />
        </div>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 opacity-0 group-hover:opacity-100 transition-all duration-300"
        >
          <MoreVertical className="h-4 w-4 text-gray-500" />
        </motion.button>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          {title}
        </h3>
        
        <div className="flex items-end justify-between">
          <motion.p 
            className="text-3xl font-bold text-gray-900 dark:text-white"
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, delay: 0.2 }}
          >
            {formatValue(value)}
          </motion.p>
          
          {trend && trendValue && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={`flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${
                trend === 'up' 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                  : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
              }`}
            >
              {trend === 'up' ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              <span>{trendValue}%</span>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Enhanced Chart Card
export const EnhancedChartCard = ({
  title,
  subtitle,
  action,
  children,
  className = "",
  ...props
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    whileHover={{ y: -2 }}
    className={`bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-lg hover:shadow-2xl transition-all duration-300 group ${className}`}
    {...props}
  >
    <div className="flex items-center justify-between mb-6">
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {subtitle}
          </p>
        )}
      </div>
      {action && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        >
          {action}
        </motion.div>
      )}
    </div>

    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="h-64 relative"
    >
      {children}
    </motion.div>
  </motion.div>
);

// Enhanced Progress Card
export const EnhancedProgressCard = ({
  title,
  value,
  color = "blue",
  description,
  className = "",
  showPercentage = true,
  ...props
}) => {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    green: "from-green-500 to-green-600",
    purple: "from-purple-500 to-purple-600",
    orange: "from-orange-500 to-orange-600",
    red: "from-red-500 to-red-600"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2, scale: 1.02 }}
      className={`bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-lg hover:shadow-2xl transition-all duration-300 group ${className}`}
      {...props}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
          {title}
        </h3>
        {showPercentage && (
          <motion.span 
            className="text-2xl font-bold text-gray-900 dark:text-white"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, delay: 0.2 }}
          >
            {value}%
          </motion.span>
        )}
      </div>

      <div className="space-y-3">
        <div className="relative">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${value}%` }}
              transition={{ duration: 1.5, ease: "easeInOut", delay: 0.3 }}
              className={`h-full bg-gradient-to-r ${colorClasses[color]} rounded-full relative`}
            >
              <motion.div
                animate={{ x: [0, 100, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
              />
            </motion.div>
          </div>
        </div>

        {description && (
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-xs text-gray-600 dark:text-gray-400"
          >
            {description}
          </motion.p>
        )}
      </div>
    </motion.div>
  );
};

// Enhanced Status Card
export const EnhancedStatusCard = ({
  title,
  status,
  icon: Icon,
  details = [],
  className = "",
  ...props
}) => {
  const statusColors = {
    online: {
      bg: "bg-green-100 dark:bg-green-900/30",
      text: "text-green-700 dark:text-green-400",
      dot: "bg-green-500",
      ring: "ring-green-500/20"
    },
    offline: {
      bg: "bg-red-100 dark:bg-red-900/30", 
      text: "text-red-700 dark:text-red-400",
      dot: "bg-red-500",
      ring: "ring-red-500/20"
    },
    warning: {
      bg: "bg-yellow-100 dark:bg-yellow-900/30",
      text: "text-yellow-700 dark:text-yellow-400", 
      dot: "bg-yellow-500",
      ring: "ring-yellow-500/20"
    }
  };

  const colors = statusColors[status] || statusColors.offline;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className={`bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-lg hover:shadow-2xl transition-all duration-300 ${className}`}
      {...props}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-xl ${colors.bg}`}>
            <Icon className={`h-5 w-5 ${colors.text}`} />
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white">{title}</h3>
            <div className="flex items-center space-x-2">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className={`w-2 h-2 ${colors.dot} rounded-full`}
              />
              <span className={`text-sm font-medium capitalize ${colors.text}`}>
                {status}
              </span>
            </div>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <Settings className="h-4 w-4 text-gray-500" />
        </motion.button>
      </div>

      {details.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-2"
        >
          {details.map((detail, index) => (
            <div key={index} className="flex justify-between items-center text-sm">
              <span className="text-gray-600 dark:text-gray-400">{detail.label}</span>
              <span className="font-medium text-gray-900 dark:text-white">{detail.value}</span>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
};

export {
  EnhancedMetricCard as MetricCard,
  EnhancedChartCard as ChartCard, 
  EnhancedProgressCard as ProgressCard,
  EnhancedStatusCard as StatusCard
};
