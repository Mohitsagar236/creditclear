/**
 * Dashboard Component
 * Main dashboard for credit risk prediction system
 */

import { useState, useEffect } from 'react';
import PredictionForm from '../components/PredictionForm.jsx';
import PredictionResults from '../components/PredictionResults.jsx';
import AutomaticDataCollectionDemo from '../components/AutomaticDataCollectionDemo.jsx';
import { checkApiHealth } from '../services/api.js';

const Dashboard = ({ setIsLoading }) => {
  const [currentView, setCurrentView] = useState('overview'); // 'overview' | 'form' | 'results' | 'comprehensive'
  const [taskId, setTaskId] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [dashboardStats, setDashboardStats] = useState({
    totalAssessments: 1247,
    pendingReviews: 23,
    modelAccuracy: 98.2,
    avgProcessingTime: 1.3
  });

  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    if (setIsLoading) setIsLoading(true);
    try {
      await checkApiHealth();
      setApiStatus('connected');
    } catch {
      setApiStatus('disconnected');
      setError('Unable to connect to the API server. Please ensure the backend is running.');
    } finally {
      if (setIsLoading) setIsLoading(false);
    }
  };

  const handlePredictionStart = (newTaskId) => {
    setTaskId(newTaskId);
    setCurrentView('results');
    setError(null);
  };

  const handleNewPrediction = () => {
    setCurrentView('form');
    setTaskId(null);
    setError(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  const getStatusIndicator = () => {
    const statusConfig = {
      checking: { class: 'status-checking', text: 'Checking...', color: '#ffa500' },
      connected: { class: 'status-connected', text: 'Connected', color: '#10b981' },
      disconnected: { class: 'status-disconnected', text: 'Disconnected', color: '#ef4444' }
    };
    
    return statusConfig[apiStatus] || statusConfig.checking;
  };

  const status = getStatusIndicator();

  // Debug logging
  console.log('Dashboard render:', { currentView, apiStatus, taskId });

  // Overview Dashboard Component
  const OverviewDashboard = () => (
    <div className="dashboard-overview">
      <h2 style={{ color: 'var(--text-primary)', marginBottom: '2rem' }}>Dashboard Overview</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-number">{dashboardStats.totalAssessments.toLocaleString()}</div>
            <div className="stat-label">Total Assessments</div>
            <div className="stat-change positive">↗ +12% this month</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-number">{dashboardStats.pendingReviews}</div>
            <div className="stat-label">Pending Reviews</div>
            <div className="stat-change neutral">→ Same as yesterday</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-number">{dashboardStats.modelAccuracy}%</div>
            <div className="stat-label">Model Accuracy</div>
            <div className="stat-change positive">↗ +0.3% this week</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-number">{dashboardStats.avgProcessingTime}s</div>
            <div className="stat-label">Avg Processing Time</div>
            <div className="stat-change positive">↘ -0.2s this week</div>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-grid">
          <button 
            className="action-card primary"
            onClick={() => setCurrentView('form')}
          >
            <div className="action-icon">📝</div>
            <div className="action-text">
              <div className="action-title">New Assessment</div>
              <div className="action-desc">Start a new credit risk evaluation</div>
            </div>
          </button>
          
          <button 
            className="action-card secondary"
            onClick={() => setCurrentView('comprehensive')}
          >
            <div className="action-icon">🤖</div>
            <div className="action-text">
              <div className="action-title">Smart Collection</div>
              <div className="action-desc">Automatic data gathering</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="modern-dashboard">
      {/* Navigation Tabs */}
      <div className="dashboard-nav-tabs">
        <button
          onClick={() => setCurrentView('overview')}
          className={`nav-tab ${currentView === 'overview' ? 'active' : ''}`}
        >
          📊 Overview
        </button>
        
        <button
          onClick={() => setCurrentView('form')}
          className={`nav-tab ${currentView === 'form' ? 'active' : ''}`}
        >
          � Risk Assessment
        </button>
        
        <button
          onClick={() => setCurrentView('comprehensive')}
          className={`nav-tab ${currentView === 'comprehensive' ? 'active' : ''}`}
        >
          🤖 Smart Data Collection
        </button>
        
        {taskId && (
          <button
            onClick={() => setCurrentView('results')}
            className={`nav-tab ${currentView === 'results' ? 'active' : ''}`}
          >
            📈 Results
          </button>
        )}
        
        <div className="api-status-indicator">
          <div className={`status-dot ${status.class}`} style={{ backgroundColor: status.color }}></div>
          <span>API {status.text}</span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="error-close"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="dashboard-content">
        {apiStatus === 'disconnected' ? (
          <div className="connection-error">
            <div className="error-icon">🔌</div>
            <h2>Connection Required</h2>
            <p>Please ensure the backend API server is running and accessible.</p>
            <div className="connection-help">
              <h4>To start the backend server:</h4>
              <pre>
                cd credit-risk-model{'\n'}
                uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
              </pre>
            </div>
            <button 
              onClick={checkApiConnection}
              className="btn btn-primary"
            >
              Check Connection Again
            </button>
          </div>
        ) : (
          <>
            {currentView === 'overview' && <OverviewDashboard />}
            
            {currentView === 'form' && (
              <PredictionForm
                onPredictionStart={handlePredictionStart}
                onError={handleError}
              />
            )}
            
            {currentView === 'comprehensive' && (
              <AutomaticDataCollectionDemo />
            )}
            
            {currentView === 'results' && taskId && (
              <PredictionResults
                taskId={taskId}
                onNewPrediction={handleNewPrediction}
                onError={handleError}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
