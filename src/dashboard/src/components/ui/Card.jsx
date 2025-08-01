/**
 * Enhanced Card Components with Various Layouts
 */
import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

// Base Card Component
export const Card = ({ 
  children, 
  className = '', 
  hover = true, 
  padding = 'p-6',
  ...props 
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={hover ? { y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" } : {}}
    className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 ${padding} ${className}`}
    {...props}
  >
    {children}
  </motion.div>
);

// Metric Card with Trend
export const MetricCard = ({ 
  title, 
  value, 
  trend, 
  trendValue, 
  icon: Icon, 
  color = 'blue',
  format = 'number',
  className = ''
}) => {
  const colorClasses = {
    blue: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-600 dark:text-blue-400', icon: 'text-blue-600 dark:text-blue-400' },
    green: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-600 dark:text-green-400', icon: 'text-green-600 dark:text-green-400' },
    red: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-600 dark:text-red-400', icon: 'text-red-600 dark:text-red-400' },
    yellow: { bg: 'bg-yellow-100 dark:bg-yellow-900', text: 'text-yellow-600 dark:text-yellow-400', icon: 'text-yellow-600 dark:text-yellow-400' },
    purple: { bg: 'bg-purple-100 dark:bg-purple-900', text: 'text-purple-600 dark:text-purple-400', icon: 'text-purple-600 dark:text-purple-400' },
  };

  const getTrendIcon = () => {
    if (trend === 'up') return TrendingUp;
    if (trend === 'down') return TrendingDown;
    return Minus;
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600 dark:text-green-400';
    if (trend === 'down') return 'text-red-600 dark:text-red-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  const formatValue = (val) => {
    if (format === 'currency') return `$${val.toLocaleString()}`;
    if (format === 'percentage') return `${val}%`;
    return val.toLocaleString();
  };

  const TrendIcon = getTrendIcon();
  const colors = colorClasses[color];

  return (
    <Card className={className}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
            {formatValue(value)}
          </p>
          {trend && trendValue && (
            <div className={`flex items-center mt-2 text-sm ${getTrendColor()}`}>
              <TrendIcon className="h-4 w-4 mr-1" />
              <span>{formatValue(trendValue)} from yesterday</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-full ${colors.bg}`}>
            <Icon className={`h-6 w-6 ${colors.icon}`} />
          </div>
        )}
      </div>
    </Card>
  );
};

// Progress Card
export const ProgressCard = ({ 
  title, 
  value, 
  maxValue = 100, 
  color = 'blue', 
  showPercentage = true,
  className = ''
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    yellow: 'bg-yellow-600',
    purple: 'bg-purple-600',
  };

  return (
    <Card className={className}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>
        {showPercentage && (
          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {percentage.toFixed(1)}%
          </span>
        )}
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-2 rounded-full ${colorClasses[color]}`}
        />
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
        <span>{value}</span>
        <span>{maxValue}</span>
      </div>
    </Card>
  );
};

// Chart Card
export const ChartCard = ({ 
  title, 
  subtitle, 
  children, 
  action,
  className = ''
}) => (
  <Card className={className}>
    <div className="flex items-center justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
        {subtitle && (
          <p className="text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>
        )}
      </div>
      {action}
    </div>
    <div className="h-64">
      {children}
    </div>
  </Card>
);

// Feature Card
export const FeatureCard = ({ 
  icon: Icon, 
  title, 
  description, 
  action,
  className = ''
}) => (
  <Card className={`text-center ${className}`}>
    {Icon && (
      <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full w-fit mx-auto mb-4">
        <Icon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
      </div>
    )}
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
    <p className="text-gray-600 dark:text-gray-400 mb-4">{description}</p>
    {action}
  </Card>
);

// List Card
export const ListCard = ({ 
  title, 
  items = [], 
  renderItem,
  emptyMessage = "No items to display",
  className = ''
}) => (
  <Card className={className}>
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">{title}</h3>
    {items.length > 0 ? (
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            {renderItem ? renderItem(item, index) : (
              <span className="text-gray-900 dark:text-gray-100">{item}</span>
            )}
          </div>
        ))}
      </div>
    ) : (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        {emptyMessage}
      </div>
    )}
  </Card>
);

export default Card;
