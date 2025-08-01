/**
 * Enhanced Dashboard with Modern UI/UX
 */
import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
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
  Filler
} from 'chart.js';
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
  RefreshCw,
  Eye,
  Settings,
  Download,
  Filter
} from 'lucide-react';
import { api } from '../../services/api';
import { MetricCard, ChartCard, ProgressCard } from '../ui/Card';
import Button, { IconButton, ButtonGroup } from '../ui/Button';
import { SkeletonCard, SkeletonChart, DataPlaceholder } from '../ui/LoadingComponents';

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
  ArcElement,
  Filler
);

const EnhancedDashboard = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [cacheStats, setCacheStats] = useState(null);
  const [requestStats, setRequestStats] = useState(null);
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

  // Enhanced chart configurations
  const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: realTimeMode ? 300 : 1000,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
        }
      },
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  };

  const lineChartOptions = {
    ...commonChartOptions,
    plugins: {
      ...commonChartOptions.plugins,
      title: {
        display: true,
        text: 'Prediction Requests Over Time',
        font: { size: 16, weight: 'bold' }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const doughnutOptions = {
    ...commonChartOptions,
    plugins: {
      ...commonChartOptions.plugins,
      title: {
        display: true,
        text: 'System Resources',
        font: { size: 16, weight: 'bold' }
      },
    },
    cutout: '60%',
  };

  // Enhanced mock data with better visualization
  const mockLineData = {
    labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
    datasets: [
      {
        label: 'Total Predictions',
        data: [12, 19, 15, 25, 22, 30, 28],
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#3B82F6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
      },
      {
        label: 'Successful',
        data: [10, 17, 13, 23, 20, 28, 26],
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#10B981',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
      },
      {
        label: 'Failed',
        data: [2, 2, 2, 2, 2, 2, 2],
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#EF4444',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
      },
    ],
  };

  const mockDoughnutData = {
    labels: ['CPU Usage', 'Memory', 'Disk I/O', 'Available'],
    datasets: [
      {
        label: 'Resource Usage %',
        data: [45, 62, 28, 35],
        backgroundColor: [
          '#EF4444',
          '#F59E0B',
          '#3B82F6',
          '#10B981',
        ],
        borderColor: [
          '#DC2626',
          '#D97706',
          '#2563EB',
          '#059669',
        ],
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const timeRanges = [
    { value: '1h', label: '1 Hour' },
    { value: '6h', label: '6 Hours' },
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div 
        className="p-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Enhanced Header */}
        <div 
          className="mb-8"
          variants={itemVariants}
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                Analytics Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                Real-time system monitoring and insights
              </p>
            </div>
            
            <div className="flex flex-wrap items-center gap-3">
              {/* Time Range Selector */}
              <ButtonGroup>
                {timeRanges.map((range) => (
                  <Button
                    key={range.value}
                    variant={selectedTimeRange === range.value ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedTimeRange(range.value)}
                  >
                    {range.label}
                  </Button>
                ))}
              </ButtonGroup>

              {/* Controls */}
              <div className="flex items-center gap-2">
                <label 
                  className="flex items-center space-x-2 cursor-pointer bg-white dark:bg-gray-800 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <input
                    type="checkbox"
                    checked={realTimeMode}
                    onChange={(e) => setRealTimeMode(e.target.checked)}
                    className="form-checkbox h-4 w-4 text-blue-600 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Live</span>
                </label>

                <IconButton
                  icon={RefreshCw}
                  onClick={refreshData}
                  variant="outline"
                  size="md"
                />

                <IconButton
                  icon={Download}
                  variant="outline"
                  size="md"
                />

                <IconButton
                  icon={Settings}
                  variant="outline"
                  size="md"
                />
              </div>

              {/* Health indicator */}
              <div 
                className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
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
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metricsLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))
          ) : (
            <>
              <MetricCard
                title="Total Predictions"
                value={metricsData?.total_predictions || 1247}
                trend="up"
                trendValue={12}
                icon={Activity}
                color="blue"
              />

              <MetricCard
                title="Active Users"
                value={metricsData?.active_users || 89}
                trend="up"
                trendValue={5}
                icon={Users}
                color="green"
              />

              <MetricCard
                title="Success Rate"
                value={94.2}
                trend="up"
                trendValue={2.1}
                icon={CheckCircle}
                color="green"
                format="percentage"
              />

              <MetricCard
                title="Avg Response Time"
                value={247}
                trend="down"
                trendValue={23}
                icon={Clock}
                color="yellow"
              />
            </>
          )}
        </div>

        {/* Enhanced Charts Section */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
          {/* Main Line Chart */}
          <div className="xl:col-span-2">
            {metricsLoading ? (
              <SkeletonChart />
            ) : (
              <ChartCard
                title="Request Analytics"
                subtitle="Real-time prediction request trends"
                action={
                  <div className="flex items-center space-x-2">
                    <IconButton icon={Eye} variant="ghost" size="sm" />
                    <IconButton icon={Filter} variant="ghost" size="sm" />
                  </div>
                }
              >
                <Line data={mockLineData} options={lineChartOptions} />
              </ChartCard>
            )}
          </div>

          {/* Resource Usage Chart */}
          <div>
            {metricsLoading ? (
              <SkeletonChart />
            ) : (
              <ChartCard
                title="System Resources"
                subtitle="Current utilization"
              >
                <Doughnut data={mockDoughnutData} options={doughnutOptions} />
              </ChartCard>
            )}
          </div>
        </div>

        {/* Progress Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <ProgressCard
            title="Database Performance"
            value={87}
            color="green"
            className="hover:shadow-xl transition-shadow duration-300"
          />

          <ProgressCard
            title="Cache Hit Rate"
            value={94}
            color="blue"
            className="hover:shadow-xl transition-shadow duration-300"
          />

          <ProgressCard
            title="Model Accuracy"
            value={96}
            color="purple"
            className="hover:shadow-xl transition-shadow duration-300"
          />
        </div>

        {/* Enhanced System Status */}
        <div 
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
          variants={itemVariants}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">System Status</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">All systems operational</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: 'API Gateway', status: 'Operational', icon: Wifi, color: 'green' },
              { name: 'Database', status: 'Connected', icon: Database, color: 'green' },
              { name: 'ML Models', status: 'Ready', icon: Activity, color: 'green' },
              { name: 'Cache Layer', status: 'Active', icon: Server, color: 'green' },
            ].map((service, index) => (
              <div
                key={service.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <service.icon className={`h-5 w-5 text-${service.color}-500`} />
                  <span className="font-medium text-gray-900 dark:text-white">{service.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 bg-${service.color}-500 rounded-full`}></div>
                  <span className={`text-sm text-${service.color}-600 dark:text-${service.color}-400 font-medium`}>
                    {service.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;
