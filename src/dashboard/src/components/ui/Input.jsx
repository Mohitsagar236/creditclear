/**
 * Enhanced Input Component System
 */
import React, { forwardRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Search, AlertCircle, CheckCircle, Info } from 'lucide-react';

// Base Input Component
export const Input = forwardRef(({
  label,
  error,
  success,
  hint,
  icon: Icon,
  className = '',
  type = 'text',
  size = 'md',
  variant = 'default',
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword && showPassword ? 'text' : type;

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-5 py-4 text-lg'
  };

  const variantClasses = {
    default: 'border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-200',
    filled: 'bg-gray-100 dark:bg-gray-700 border-transparent focus:bg-white dark:focus:bg-gray-600',
    underline: 'border-0 border-b-2 border-gray-300 dark:border-gray-600 rounded-none focus:ring-0'
  };

  const baseClasses = `
    w-full rounded-lg transition-all duration-200 
    bg-white dark:bg-gray-800 text-gray-900 dark:text-white
    disabled:opacity-50 disabled:cursor-not-allowed
    placeholder:text-gray-500 dark:placeholder:text-gray-400
    ${sizeClasses[size]}
    ${variantClasses[variant]}
    ${error ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : ''}
    ${success ? 'border-green-300 focus:border-green-500 focus:ring-green-200' : ''}
    ${Icon ? 'pl-12' : ''}
    ${isPassword ? 'pr-12' : ''}
    ${className}
  `;

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        )}
        
        <input
          ref={ref}
          type={inputType}
          className={baseClasses}
          {...props}
        />
        
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        )}
      </div>
      
      {(error || success || hint) && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start space-x-2"
        >
          {error && (
            <>
              <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
            </>
          )}
          {success && (
            <>
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-green-600 dark:text-green-400">{success}</span>
            </>
          )}
          {hint && !error && !success && (
            <>
              <Info className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-500 dark:text-gray-400">{hint}</span>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Search Input Component
export const SearchInput = forwardRef(({
  placeholder = "Search...",
  className = '',
  onClear,
  ...props
}, ref) => {
  return (
    <Input
      ref={ref}
      icon={Search}
      placeholder={placeholder}
      className={`pr-12 ${className}`}
      {...props}
    />
  );
});

SearchInput.displayName = 'SearchInput';

// Select Component
export const Select = forwardRef(({
  label,
  error,
  success,
  hint,
  options = [],
  placeholder = "Select an option",
  className = '',
  ...props
}, ref) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <select
        ref={ref}
        className={`
          w-full px-4 py-3 rounded-lg border transition-all duration-200
          bg-white dark:bg-gray-800 text-gray-900 dark:text-white
          disabled:opacity-50 disabled:cursor-not-allowed
          ${error 
            ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
            : success 
            ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
            : 'border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-200'
          }
          ${className}
        `}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {(error || success || hint) && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start space-x-2"
        >
          {error && (
            <>
              <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
            </>
          )}
          {success && (
            <>
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-green-600 dark:text-green-400">{success}</span>
            </>
          )}
          {hint && !error && !success && (
            <>
              <Info className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-500 dark:text-gray-400">{hint}</span>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
});

Select.displayName = 'Select';

// Textarea Component
export const Textarea = forwardRef(({
  label,
  error,
  success,
  hint,
  className = '',
  rows = 4,
  ...props
}, ref) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        ref={ref}
        rows={rows}
        className={`
          w-full px-4 py-3 rounded-lg border transition-all duration-200 resize-none
          bg-white dark:bg-gray-800 text-gray-900 dark:text-white
          disabled:opacity-50 disabled:cursor-not-allowed
          placeholder:text-gray-500 dark:placeholder:text-gray-400
          ${error 
            ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
            : success 
            ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
            : 'border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-200'
          }
          ${className}
        `}
        {...props}
      />
      
      {(error || success || hint) && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start space-x-2"
        >
          {error && (
            <>
              <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
            </>
          )}
          {success && (
            <>
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-green-600 dark:text-green-400">{success}</span>
            </>
          )}
          {hint && !error && !success && (
            <>
              <Info className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-500 dark:text-gray-400">{hint}</span>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

// Range/Slider Component
export const Range = ({
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  showValue = true,
  className = '',
  ...props
}) => {
  return (
    <div className="space-y-3">
      {label && (
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </label>
          {showValue && (
            <span className="text-sm text-gray-500 dark:text-gray-400 font-mono">
              {value}
            </span>
          )}
        </div>
      )}
      
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={onChange}
          className={`
            w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
            slider:bg-blue-600 slider:rounded-lg
            ${className}
          `}
          {...props}
        />
        
        {/* Value indicators */}
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>{min}</span>
          <span>{max}</span>
        </div>
      </div>
    </div>
  );
};

// File Upload Component
export const FileUpload = ({
  label,
  accept,
  multiple = false,
  onFileSelect,
  className = '',
  ...props
}) => {
  const [dragOver, setDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    onFileSelect?.(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    onFileSelect?.(files);
  };

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
          ${dragOver 
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
          }
          ${className}
        `}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
          {...props}
        />
        
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="space-y-2">
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div className="text-gray-600 dark:text-gray-400">
              <span className="font-medium text-blue-600 dark:text-blue-400">Click to upload</span> or drag and drop
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {accept ? `Supported: ${accept}` : 'Any file type'}
            </p>
          </div>
        </label>
      </div>
    </div>
  );
};

export default Input;
