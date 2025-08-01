/**
 * Enhanced Navigation Component with Modern Design
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Calculator,
  Settings,
  HelpCircle,
  Menu,
  X,
  Activity,
  ChevronDown,
  Bell,
  User,
  Moon,
  Sun,
  Palette,
  Brain
} from 'lucide-react';
import { useTheme } from '../../contexts/EnhancedThemeContext';
import Button from './Button';

const Navigation = ({ currentPage, setCurrentPage, sidebarOpen, setSidebarOpen }) => {
  const { isDarkMode, toggleDarkMode, accentColor, setAccentColor } = useTheme();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  const navItems = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: LayoutDashboard,
      description: 'Overview and analytics'
    },
    { 
      id: 'prediction', 
      label: 'Risk Assessment', 
      icon: Calculator,
      description: 'Credit risk prediction'
    },
    { 
      id: 'digital-footprint', 
      label: 'Digital Footprint', 
      icon: Activity,
      description: 'Digital identity analysis'
    },
    { 
      id: 'ai-alternative-data', 
      label: 'AI Alternative Data', 
      icon: Brain,
      description: 'AI-powered alternative data analysis'
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings,
      description: 'App configuration'
    },
    { 
      id: 'help', 
      label: 'Help', 
      icon: HelpCircle,
      description: 'Documentation & support'
    },
  ];

  const accentColors = [
    { name: 'Blue', value: 'blue', color: '#3B82F6' },
    { name: 'Green', value: 'green', color: '#10B981' },
    { name: 'Purple', value: 'purple', color: '#8B5CF6' },
    { name: 'Orange', value: 'orange', color: '#F59E0B' },
  ];

  return (
    <>
      {/* Mobile menu button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <motion.div
          initial={false}
          animate={{ rotate: sidebarOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </motion.div>
      </motion.button>

      {/* Sidebar */}
      <AnimatePresence>
        {(sidebarOpen || window.innerWidth >= 1024) && (
          <motion.nav
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed left-0 top-0 h-full w-80 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl shadow-2xl z-40 lg:relative lg:translate-x-0 border-r border-gray-200/50 dark:border-gray-700/50"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center space-x-3 mb-6">
                <motion.div 
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.6, type: "spring" }}
                  className="relative p-3 bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 rounded-2xl shadow-lg"
                >
                  <Activity className="h-6 w-6 text-white" />
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 rounded-2xl opacity-0 hover:opacity-20 transition-opacity duration-300" />
                </motion.div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    CreditClear
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Risk Assessment Platform</p>
                </div>
              </div>

              {/* Enhanced User Profile */}
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="w-full flex items-center space-x-3 p-4 rounded-2xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 hover:from-gray-100 hover:to-gray-200 dark:hover:from-gray-700 dark:hover:to-gray-600 transition-all duration-300 border border-gray-200/50 dark:border-gray-600/50"
                >
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                      <User className="h-6 w-6 text-white" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800 shadow-sm" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">John Doe</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Risk Analyst</p>
                  </div>
                  <motion.div
                    animate={{ rotate: showUserMenu ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  </motion.div>
                </motion.button>

                <AnimatePresence>
                  {showUserMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className="absolute top-full left-0 right-0 mt-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-2 z-50"
                    >
                      <motion.button 
                        whileHover={{ x: 4 }}
                        className="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50 rounded-xl transition-all duration-200"
                      >
                        Profile Settings
                      </motion.button>
                      <motion.button 
                        whileHover={{ x: 4 }}
                        className="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50 rounded-xl transition-all duration-200"
                      >
                        Logout
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Enhanced Navigation Items */}
            <div className="p-4 flex-1 overflow-y-auto">
              <div className="space-y-2">
                {navItems.map((item, index) => {
                  const Icon = item.icon;
                  const isActive = currentPage === item.id;
                  
                  return (
                    <motion.button
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      whileHover={{ x: 6, scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        setCurrentPage(item.id);
                        setSidebarOpen(false);
                      }}
                      className={`w-full flex items-center space-x-4 px-4 py-4 rounded-2xl transition-all duration-300 group relative overflow-hidden ${
                        isActive
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-2xl'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100/80 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      {/* Active indicator */}
                      {isActive && (
                        <motion.div
                          layoutId="activeTab"
                          className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl"
                          transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        />
                      )}
                      
                      {/* Hover effect */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                        initial={{ scale: 0.8 }}
                        whileHover={{ scale: 1 }}
                      />
                      
                      <div className="relative z-10 flex items-center space-x-4 w-full">
                        <motion.div
                          whileHover={{ rotate: 12, scale: 1.1 }}
                          transition={{ type: "spring", stiffness: 300 }}
                          className={`p-2 rounded-xl ${
                            isActive 
                              ? 'bg-white/20 text-white' 
                              : 'bg-gray-200/50 dark:bg-gray-700/50 group-hover:bg-blue-100/50 dark:group-hover:bg-blue-900/30'
                          }`}
                        >
                          <Icon className="h-5 w-5" />
                        </motion.div>
                        <div className="flex-1 text-left">
                          <p className={`font-semibold text-sm ${isActive ? 'text-white' : ''}`}>
                            {item.label}
                          </p>
                          <p className={`text-xs ${
                            isActive 
                              ? 'text-blue-100' 
                              : 'text-gray-500 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400'
                          }`}>
                            {item.description}
                          </p>
                        </div>
                        
                        {/* Arrow indicator for active item */}
                        <AnimatePresence>
                          {isActive && (
                            <motion.div
                              initial={{ opacity: 0, scale: 0 }}
                              animate={{ opacity: 1, scale: 1 }}
                              exit={{ opacity: 0, scale: 0 }}
                              className="w-2 h-2 bg-white rounded-full"
                            />
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Enhanced Theme Controls */}
            <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50">
              <div className="space-y-4">
                {/* Dark Mode Toggle */}
                <div className="flex items-center justify-between p-3 bg-gray-50/50 dark:bg-gray-800/50 rounded-2xl">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark Mode</span>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={toggleDarkMode}
                    className={`relative p-2 rounded-xl transition-all duration-300 ${
                      isDarkMode 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    <motion.div
                      animate={{ rotate: isDarkMode ? 180 : 0 }}
                      transition={{ duration: 0.5, type: "spring" }}
                    >
                      {isDarkMode ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                    </motion.div>
                    {isDarkMode && (
                      <motion.div 
                        className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-xl opacity-50"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    )}
                  </motion.button>
                </div>

                {/* Enhanced Color Theme */}
                <div className="p-3 bg-gray-50/50 dark:bg-gray-800/50 rounded-2xl">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Theme Color</span>
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setShowThemeMenu(!showThemeMenu)}
                      className="p-2 rounded-xl bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    >
                      <motion.div
                        animate={{ rotate: showThemeMenu ? 180 : 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Palette className="h-4 w-4" />
                      </motion.div>
                    </motion.button>
                  </div>
                  
                  <AnimatePresence>
                    {showThemeMenu && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="grid grid-cols-4 gap-2"
                      >
                        {accentColors.map((color, index) => (
                          <motion.button
                            key={color.value}
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ scale: 1.2, rotate: 5 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => setAccentColor(color.value)}
                            className={`relative w-8 h-8 rounded-2xl border-2 transition-all duration-300 ${
                              accentColor === color.value 
                                ? 'border-gray-800 dark:border-white shadow-lg' 
                                : 'border-gray-300 dark:border-gray-600 hover:border-gray-500'
                            }`}
                            style={{ backgroundColor: color.color }}
                          >
                            {accentColor === color.value && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="absolute inset-0 border-2 border-white rounded-2xl"
                              />
                            )}
                          </motion.button>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </div>

            {/* Enhanced Version Info */}
            <div className="p-4 text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Version 2.0.0</p>
                  <p>© 2024 CreditClear</p>
                </div>
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-2 h-2 bg-green-500 rounded-full"
                />
              </div>
            </div>
          </motion.nav>
        )}
      </AnimatePresence>

      {/* Overlay for mobile */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          />
        )}
      </AnimatePresence>
    </>
  );
};

export default Navigation;
