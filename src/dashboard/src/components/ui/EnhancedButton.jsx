/**
 * Enhanced Button Components with Modern UI/UX
 */
import React from 'react';
import { motion } from 'framer-motion';
import { EnhancedButtonLoader } from './EnhancedLoadingComponents';

// Enhanced Button Component
export const EnhancedButton = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconPosition = "left",
  className = "",
  onClick,
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden";
  
  const variantClasses = {
    primary: "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-blue-500 shadow-lg hover:shadow-xl",
    secondary: "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-gray-400 focus:ring-gray-500 shadow-sm hover:shadow-md dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700",
    success: "bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 focus:ring-green-500 shadow-lg hover:shadow-xl",
    danger: "bg-gradient-to-r from-red-600 to-pink-600 text-white hover:from-red-700 hover:to-pink-700 focus:ring-red-500 shadow-lg hover:shadow-xl",
    warning: "bg-gradient-to-r from-orange-500 to-yellow-500 text-white hover:from-orange-600 hover:to-yellow-600 focus:ring-orange-500 shadow-lg hover:shadow-xl",
    ghost: "text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:ring-gray-300 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800",
    outline: "border-2 border-gray-300 text-gray-700 hover:border-blue-500 hover:text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:text-gray-300 dark:hover:border-blue-400 dark:hover:text-blue-400"
  };
  
  const sizeClasses = {
    sm: "px-3 py-2 text-sm rounded-xl",
    md: "px-4 py-2.5 text-sm rounded-xl", 
    lg: "px-6 py-3 text-base rounded-2xl",
    xl: "px-8 py-4 text-lg rounded-2xl"
  };

  const handleClick = (e) => {
    if (disabled || isLoading) return;
    onClick?.(e);
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || isLoading ? 1 : 1.02, y: disabled || isLoading ? 0 : -1 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || isLoading}
      onClick={handleClick}
      {...props}
    >
      {/* Shimmer effect for primary buttons */}
      {variant === 'primary' && !disabled && !isLoading && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6 }}
        />
      )}
      
      {/* Loading state */}
      {isLoading ? (
        <div className="flex items-center space-x-2">
          <EnhancedButtonLoader size={size === 'sm' ? 'sm' : size === 'lg' || size === 'xl' ? 'lg' : 'md'} />
          <span>Loading...</span>
        </div>
      ) : (
        <>
          {Icon && iconPosition === 'left' && (
            <Icon className={`${size === 'sm' ? 'h-4 w-4' : size === 'lg' || size === 'xl' ? 'h-6 w-6' : 'h-5 w-5'} ${children ? 'mr-2' : ''}`} />
          )}
          {children}
          {Icon && iconPosition === 'right' && (
            <Icon className={`${size === 'sm' ? 'h-4 w-4' : size === 'lg' || size === 'xl' ? 'h-6 w-6' : 'h-5 w-5'} ${children ? 'ml-2' : ''}`} />
          )}
        </>
      )}
    </motion.button>
  );
};

// Enhanced Icon Button
export const EnhancedIconButton = ({
  icon: Icon,
  variant = "ghost",
  size = "md",
  isLoading = false,
  disabled = false,
  className = "",
  tooltip,
  onClick,
  ...props
}) => {
  const sizeClasses = {
    sm: "p-2 rounded-xl",
    md: "p-3 rounded-xl",
    lg: "p-4 rounded-2xl"
  };

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5", 
    lg: "h-6 w-6"
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || isLoading ? 1 : 1.05 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.95 }}
      className={`inline-flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${sizeClasses[size]} ${className}`}
      disabled={disabled || isLoading}
      onClick={onClick}
      title={tooltip}
      {...props}
    >
      {isLoading ? (
        <EnhancedButtonLoader size={size} />
      ) : (
        <Icon className={iconSizes[size]} />
      )}
    </motion.button>
  );
};

// Enhanced Button Group
export const EnhancedButtonGroup = ({ children, className = "", ...props }) => (
  <div className={`inline-flex rounded-2xl border border-gray-200 dark:border-gray-600 overflow-hidden bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl shadow-lg ${className}`} {...props}>
    {React.Children.map(children, (child, index) => {
      if (!React.isValidElement(child)) return child;
      
      return React.cloneElement(child, {
        className: `${child.props.className || ''} rounded-none border-0 ${
          index > 0 ? 'border-l border-gray-200 dark:border-gray-600' : ''
        }`
      });
    })}
  </div>
);

// Enhanced Floating Action Button
export const EnhancedFloatingButton = ({
  icon: Icon,
  onClick,
  variant = "primary",
  size = "md",
  position = "bottom-right",
  className = "",
  ...props
}) => {
  const positionClasses = {
    "bottom-right": "fixed bottom-6 right-6",
    "bottom-left": "fixed bottom-6 left-6",
    "top-right": "fixed top-6 right-6", 
    "top-left": "fixed top-6 left-6"
  };

  const sizeClasses = {
    sm: "w-12 h-12",
    md: "w-16 h-16",
    lg: "w-20 h-20"
  };

  const iconSizes = {
    sm: "h-5 w-5",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  return (
    <motion.button
      initial={{ scale: 0, rotate: 180 }}
      animate={{ scale: 1, rotate: 0 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className={`${positionClasses[position]} ${sizeClasses[size]} bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/50 z-50 ${className}`}
      onClick={onClick}
      {...props}
    >
      <Icon className={`${iconSizes[size]} mx-auto`} />
    </motion.button>
  );
};

export {
  EnhancedButton as Button,
  EnhancedIconButton as IconButton,
  EnhancedButtonGroup as ButtonGroup,
  EnhancedFloatingButton as FloatingButton
};
