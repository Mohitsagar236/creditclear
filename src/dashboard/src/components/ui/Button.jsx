/**
 * Enhanced Button Components with Multiple Variants
 */
import React from 'react';
import { motion } from 'framer-motion';
import { ButtonSpinner } from './LoadingComponents';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  onClick,
  type = 'button',
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500 shadow-md hover:shadow-lg",
    secondary: "bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500 shadow-md hover:shadow-lg",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus:ring-blue-500",
    ghost: "text-blue-600 hover:bg-blue-50 focus:ring-blue-500",
    danger: "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 shadow-md hover:shadow-lg",
    success: "bg-green-600 hover:bg-green-700 text-white focus:ring-green-500 shadow-md hover:shadow-lg",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
    xl: "px-8 py-4 text-xl",
  };

  const combinedClasses = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;

  return (
    <motion.button
      whileHover={{ scale: disabled || isLoading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      className={combinedClasses}
      disabled={disabled || isLoading}
      onClick={onClick}
      type={type}
      {...props}
    >
      {isLoading ? (
        <>
          <ButtonSpinner size={size === 'sm' ? 'sm' : size === 'lg' || size === 'xl' ? 'lg' : 'md'} />
          <span className="ml-2">Loading...</span>
        </>
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon className="mr-2 h-5 w-5" />}
          {children}
          {Icon && iconPosition === 'right' && <Icon className="ml-2 h-5 w-5" />}
        </>
      )}
    </motion.button>
  );
};

// Floating Action Button
export const FloatingActionButton = ({ children, onClick, className = "", ...props }) => (
  <motion.button
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.9 }}
    className={`fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`}
    onClick={onClick}
    {...props}
  >
    {children}
  </motion.button>
);

// Icon Button
export const IconButton = ({ 
  icon: Icon, 
  variant = 'ghost', 
  size = 'md', 
  className = '', 
  ...props 
}) => {
  const sizes = {
    sm: "p-1.5",
    md: "p-2",
    lg: "p-3",
  };

  return (
    <Button
      variant={variant}
      className={`${sizes[size]} ${className}`}
      {...props}
    >
      <Icon className="h-5 w-5" />
    </Button>
  );
};

// Button Group
export const ButtonGroup = ({ children, className = "" }) => (
  <div className={`inline-flex rounded-lg shadow-sm ${className}`}>
    {React.Children.map(children, (child, index) => {
      if (!React.isValidElement(child)) return child;
      
      const isFirst = index === 0;
      const isLast = index === React.Children.count(children) - 1;
      
      return React.cloneElement(child, {
        className: `${child.props.className || ''} ${
          isFirst ? 'rounded-r-none' : isLast ? 'rounded-l-none' : 'rounded-none'
        } ${!isFirst ? '-ml-px' : ''}`,
      });
    })}
  </div>
);

export default Button;
