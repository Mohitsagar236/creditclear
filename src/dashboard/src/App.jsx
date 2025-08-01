/**
 * Enhanced Main App Component with Modern UI/UX
 */
import React, { Suspense, useState } from 'react';        
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';  
import { ThemeProvider } from './contexts/EnhancedThemeContext';
import { PageLoader } from './components/ui/LoadingComponents';
import Navigation from './components/ui/Navigation';

// Lazy load components
const ModernDashboard = React.lazy(() => import('./components/Dashboard/ModernDashboard'));
const EnhancedPredictionForm = React.lazy(() => import('./components/Forms/EnhancedPredictionForm'));
const DigitalFootprintDisplay = React.lazy(() => import('./components/DigitalFootprintDisplay.jsx'));
const AIAlternativeDataDemo = React.lazy(() => import('./components/AIAlternativeDataDemo.jsx'));

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };        
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-100 dark:from-gray-900 dark:to-gray-800">   
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg max-w-md border border-gray-200 dark:border-gray-700"
          >
            <div className="text-red-500 mb-4">
              <svg className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              We apologize for the inconvenience. Please refresh the page or try again later.
            </p>
            <button
              onClick={() => window.location.reload()}    
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Refresh Page
            </button>
          </motion.div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);  
  
  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <ModernDashboard />;
      case 'prediction':
        return (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
            <div className="max-w-4xl mx-auto">
              <EnhancedPredictionForm
                onPredictionComplete={(result) => {       
                  console.log('Prediction completed:', result);
                }}
              />
            </div>
          </div>
        );
      case 'digital-footprint':
        return (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
            <div className="max-w-6xl mx-auto">
              <DigitalFootprintDisplay />
            </div>
          </div>
        );
      case 'ai-alternative-data':
        return (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
            <div className="max-w-7xl mx-auto">
              <AIAlternativeDataDemo />
            </div>
          </div>
        );
      case 'settings':
        return (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Settings</h2>
              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">API Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        API Base URL
                      </label>
                      <input
                        type="text"
                        defaultValue="http://localhost:8001"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Backend server endpoint (currently running on port 8001)
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Request Timeout (ms)
                      </label>
                      <input
                        type="number"
                        defaultValue="30000"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Maximum time to wait for API responses
                      </p>
                    </div>
                  </div>
                </div>

                {/* Server Status Section */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Server Status</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">Frontend Server</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">React Development Server</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="text-sm font-medium text-green-600 dark:text-green-400">Online</span>
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          <span className="font-mono bg-gray-200 dark:bg-gray-800 px-2 py-1 rounded text-xs">http://localhost:3004</span>
                        </p>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">Backend API</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">FastAPI Server</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="text-sm font-medium text-green-600 dark:text-green-400">Online</span>
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          <span className="font-mono bg-gray-200 dark:bg-gray-800 px-2 py-1 rounded text-xs">http://localhost:8001</span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Application Information */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Application Information</h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Version</h4>
                        <p className="text-lg font-mono text-blue-600 dark:text-blue-400">2.0.0</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Enhanced UI/UX Version</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Environment</h4>
                        <p className="text-lg font-mono text-green-600 dark:text-green-400">Development</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Local Development Mode</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Last Updated</h4>
                        <p className="text-lg font-mono text-purple-600 dark:text-purple-400">2025-07-30</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Latest Enhancement</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Display Preferences Section */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Display Preferences</h3>
                  <div className="space-y-4">
                    <label className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                      <input type="checkbox" defaultChecked className="form-checkbox h-5 w-5 text-blue-600 rounded" />      
                      <div>
                        <span className="text-gray-900 dark:text-white font-medium">Enable real-time updates</span>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Automatically refresh data every few seconds</p>
                      </div>
                    </label>
                    <label className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                      <input type="checkbox" defaultChecked className="form-checkbox h-5 w-5 text-blue-600 rounded" />      
                      <div>
                        <span className="text-gray-900 dark:text-white font-medium">Show detailed error messages</span>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Display technical details when errors occur</p>
                      </div>
                    </label>
                    <label className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                      <input type="checkbox" className="form-checkbox h-5 w-5 text-blue-600 rounded" />
                      <div>
                        <span className="text-gray-900 dark:text-white font-medium">Enable notifications</span>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Receive alerts for important system events</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        );
      case 'help':
        return (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Help & Documentation</h2>
              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Getting Started</h3>
                  <div className="prose dark:prose-invert max-w-none">
                    <p className="text-gray-600 dark:text-gray-400 mb-4">      
                      Welcome to CreditClear! This application helps you assess credit risk using advanced machine learning models.
                    </p>
                    <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-400">
                      <li>Navigate to "Risk Assessment" to make predictions</li>
                      <li>View system health and metrics on the Dashboard</li>
                      <li>Analyze digital footprints for enhanced risk assessment</li>
                      <li>Configure settings to customize your experience</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Frequently Asked Questions</h3>
                  <div className="space-y-6">
                    {[
                      {
                        question: "How accurate are the predictions?",
                        answer: "Our models are trained on extensive datasets and achieve high accuracy rates. Results include confidence scores to help you assess reliability."
                      },
                      {
                        question: "What data is required for assessment?",
                        answer: "Basic financial information including income, credit amount, employment history, and optional external scores."
                      },
                      {
                        question: "How is my data protected?",
                        answer: "We use industry-standard encryption and security practices to protect all sensitive information."
                      }
                    ].map((faq, index) => (
                      <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{faq.question}</h4>
                        <p className="text-gray-600 dark:text-gray-400">{faq.answer}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        );
      default:
        return <ModernDashboard />;
    }
  };
  
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">        
            <Navigation
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              sidebarOpen={sidebarOpen}
              setSidebarOpen={setSidebarOpen}
            />
            <main className="flex-1 overflow-auto">
              <Suspense fallback={<PageLoader message="Loading page..." />}>      
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentPage}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className="h-full"
                  >
                    {renderPage()}
                  </motion.div>
                </AnimatePresence>
              </Suspense>
            </main>
          </div>
          
          {/* Enhanced Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--toast-bg)',
                color: 'var(--toast-color)',
                borderRadius: '12px',
                border: '1px solid var(--toast-border)',
                fontSize: '14px',
                fontWeight: '500',
              },
              success: {
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#ffffff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#ffffff',
                },
              },
            }}
          />
          
          {/* React Query Devtools */}
          <ReactQueryDevtools initialIsOpen={false} />      
        </QueryClientProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;
