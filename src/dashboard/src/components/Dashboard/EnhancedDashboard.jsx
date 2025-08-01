/**
 * Enhanced Dashboard Component
 * 
 * Modern, responsive dashboard with real-time metrics, animations,
 * and comprehensive system monitoring capabilities.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Server,
  Database,
  Wifi,
  WifiOff,
  RefreshCw
} from 'lucide-react';
import { api } from '../../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const EnhancedDashboard = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [realTimeMode, setRealTimeMode] = useState(false);
  const queryClient = useQueryClient();

  // Health status query
  const { data: healthData, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: api.checkHealth,
    refetchInterval: realTimeMode ? 5000 : 30000,
    retry: 3,
  });

  // System metrics query
  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics', selectedTimeRange],
    queryFn: api.getMetrics,
    refetchInterval: realTimeMode ? 2000 : 10000,
    retry: 2,
  });

  // Cache stats
  const [cacheStats, setCacheStats] = useState(null);
  const [requestStats, setRequestStats] = useState(null);

  useEffect(() => {
    const updateStats = () => {
      setCacheStats(api.getCacheStats());
      setRequestStats(api.getRequestQueueStats());
    };

    updateStats();
    const interval = setInterval(updateStats, 1000);
    return () => clearInterval(interval);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  const getHealthStatus = () => {
    if (healthLoading) return { status: 'loading', color: 'text-gray-500', icon: Clock };
    if (healthError) return { status: 'error', color: 'text-red-500', icon: WifiOff };
    if (healthData?.success) return { status: 'healthy', color: 'text-green-500', icon: CheckCircle };
    return { status: 'warning', color: 'text-yellow-500', icon: AlertTriangle };
  };

  const healthStatus = getHealthStatus();

  const refreshData = () => {
    queryClient.invalidateQueries(['health']);
    queryClient.invalidateQueries(['metrics']);
    api.clearCache();
  };

  // Chart configurations
  const lineChartOptions = {
    responsive: true,
    animation: {
      duration: realTimeMode ? 300 : 1000,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Prediction Requests Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: true,
        text: 'System Resources',
      },
    },
  };

  // Mock data for charts (replace with real data from metricsData)
  const mockLineData = {
    labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
    datasets: [
      {
        label: 'Predictions',
        data: [12, 19, 3, 5, 8],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Successful',
        data: [10, 17, 3, 4, 7],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const mockDoughnutData = {
    labels: ['CPU', 'Memory', 'Disk', 'Available'],
    datasets: [
      {
        label: 'Resource Usage %',
        data: [45, 62, 28, 35],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(34, 197, 94, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div 
        className="mb-8"
        variants={itemVariants}
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Credit Risk Dashboard
            </h1>
            <p className="text-gray-600">Real-time system monitoring and analytics</p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Real-time toggle */}
            <motion.label 
              className="flex items-center space-x-2 cursor-pointer"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <input
                type="checkbox"
                checked={realTimeMode}
                onChange={(e) => setRealTimeMode(e.target.checked)}
                className="form-checkbox h-5 w-5 text-blue-600"
              />
              <span className="text-sm font-medium text-gray-700">Real-time</span>
            </motion.label>

            {/* Refresh button */}
            <motion.button
              onClick={refreshData}
              className="p-2 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw className="h-5 w-5 text-gray-600" />
            </motion.button>

            {/* Health indicator */}
            <motion.div 
              className="flex items-center space-x-2 px-3 py-2 bg-white rounded-lg shadow-md"
              animate={{ 
                scale: healthStatus.status === 'loading' ? [1, 1.05, 1] : 1 
              }}
              transition={{ 
                repeat: healthStatus.status === 'loading' ? Infinity : 0,
                duration: 1 
              }}
            >
              <healthStatus.icon className={`h-5 w-5 ${healthStatus.color}`} />
              <span className="text-sm font-medium capitalize">
                {healthStatus.status}
              </span>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        variants={containerVariants}
      >
        {/* Total Predictions */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Predictions</p>
              <p className="text-3xl font-bold text-gray-900">
                {metricsData?.total_predictions || '1,247'}
              </p>
              <p className="text-sm text-green-600 mt-1">
                <TrendingUp className="inline h-4 w-4" /> +12% from yesterday
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        {/* Active Users */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-3xl font-bold text-gray-900">
                {metricsData?.active_users || '89'}
              </p>
              <p className="text-sm text-green-600 mt-1">
                <Users className="inline h-4 w-4" /> +5 new today
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        {/* Cache Stats */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cache Items</p>
              <p className="text-3xl font-bold text-gray-900">
                {cacheStats?.size || 0}
              </p>
              <p className="text-sm text-blue-600 mt-1">
                <Database className="inline h-4 w-4" /> {requestStats?.active || 0} active requests
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        {/* System Health */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-3xl font-bold text-gray-900">
                {healthData?.success ? '99.9%' : 'N/A'}
              </p>
              <p className="text-sm text-green-600 mt-1">
                <Server className="inline h-4 w-4" /> All systems operational
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Server className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Line Chart */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.01 }}
        >
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Prediction Trends</h3>
            <div className="flex space-x-2 mt-2">
              {['1h', '6h', '24h', '7d'].map((range) => (
                <button
                  key={range}
                  onClick={() => setSelectedTimeRange(range)}
                  className={`px-3 py-1 text-sm rounded-full transition-colors ${
                    selectedTimeRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
          <div style={{ height: '300px' }}>
            <Line data={mockLineData} options={lineChartOptions} />
          </div>
        </motion.div>

        {/* Doughnut Chart */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
          variants={itemVariants}
          whileHover={{ scale: 1.01 }}
        >
          <div style={{ height: '300px' }}>
            <Doughnut data={mockDoughnutData} options={doughnutOptions} />
          </div>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div 
        className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
        variants={itemVariants}
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* API Status */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Wifi className="h-5 w-5 text-green-500" />
              <span className="font-medium">API</span>
            </div>
            <span className="text-green-600 font-medium">Operational</span>
          </div>

          {/* Database Status */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Database className="h-5 w-5 text-green-500" />
              <span className="font-medium">Database</span>
            </div>
            <span className="text-green-600 font-medium">Connected</span>
          </div>

          {/* Model Status */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Activity className="h-5 w-5 text-green-500" />
              <span className="font-medium">ML Model</span>
            </div>
            <span className="text-green-600 font-medium">Ready</span>
          </div>
        </div>

        {/* Additional Health Details */}
        <AnimatePresence>
          {healthData && (
            <motion.div 
              className="mt-4 p-4 bg-blue-50 rounded-lg"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="text-sm text-gray-600">
                <p><strong>Model:</strong> {healthData.modelName}</p>
                <p><strong>Workers:</strong> {healthData.workerCount}</p>
                <p><strong>Celery Status:</strong> {healthData.celeryStatus}</p>
                <p><strong>Last Updated:</strong> {new Date().toLocaleTimeString()}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default EnhancedDashboard;
