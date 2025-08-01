/**
 * PredictionResults Component
 * Displays credit risk prediction results and explanations
 */

import { useState, useEffect } from 'react';
import { pollPredictionResult } from '../services/api.js';

const PredictionResults = ({ taskId, onNewPrediction, onError }) => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!taskId) return;

    let isMounted = true;

    const pollResults = async () => {
      try {
        const response = await pollPredictionResult(taskId, {
          maxAttempts: 30,
          intervalMs: 2000,
          onProgress: (attempt, maxAttempts) => {
            console.log(`Polling attempt ${attempt}/${maxAttempts}`);
          }
        });

        if (isMounted) {
          setResult(response);
          setIsLoading(false);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to get prediction results');
          setIsLoading(false);
          onError?.(err.message);
        }
      }
    };

    pollResults();

    return () => {
      isMounted = false;
    };
  }, [taskId, onError]);

  const getRiskLevel = (probability) => {
    if (probability < 0.3) return { level: 'Low', class: 'risk-low' };
    if (probability < 0.7) return { level: 'Medium', class: 'risk-medium' };
    return { level: 'High', class: 'risk-high' };
  };

  const formatFeatureImportance = (features) => {
    if (!features || typeof features !== 'object') return [];
    
    return Object.entries(features)
      .map(([feature, importance]) => ({
        feature: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        importance: parseFloat(importance),
        percentage: (parseFloat(importance) * 100).toFixed(1)
      }))
      .sort((a, b) => b.importance - a.importance)
      .slice(0, 10); // Show top 10 features
  };

  if (isLoading) {
    return (
      <div className="prediction-results loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Processing prediction...</p>
          <small>This may take a few moments</small>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prediction-results error">
        <div className="error-container">
          <h3>Prediction Error</h3>
          <p>{error}</p>
          <button 
            onClick={onNewPrediction}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const riskInfo = getRiskLevel(result.default_probability);
  const featureImportance = formatFeatureImportance(result.feature_importance);

  return (
    <div className="prediction-results">
      <div className="results-header">
        <h2>Credit Risk Assessment Results</h2>
        <button 
          onClick={onNewPrediction}
          className="btn btn-outline"
        >
          New Prediction
        </button>
      </div>

      {/* Main Risk Score */}
      <div className="risk-score-container">
        <div className={`risk-score ${riskInfo.class}`}>
          <div className="risk-level">
            <span className="level-text">{riskInfo.level} Risk</span>
            <span className="probability-text">
              {(result.default_probability * 100).toFixed(1)}%
            </span>
          </div>
          <div className="risk-meter">
            <div 
              className="risk-fill"
              style={{ width: `${result.default_probability * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="risk-interpretation">
          <h4>Risk Interpretation</h4>
          <p>
            {riskInfo.level === 'Low' && 
              "This applicant shows strong creditworthiness with a low probability of default. Recommended for approval with standard terms."
            }
            {riskInfo.level === 'Medium' && 
              "This applicant presents moderate risk. Consider additional verification or adjusted terms. Manual review recommended."
            }
            {riskInfo.level === 'High' && 
              "This applicant shows significant risk factors. Careful evaluation required. Consider decline or high-risk terms."
            }
          </p>
        </div>
      </div>

      {/* Model Information */}
      <div className="model-info">
        <div className="info-row">
          <div className="info-item">
            <label>Model Used:</label>
            <span>{result.model_version || 'XGBoost v1.0'}</span>
          </div>
          <div className="info-item">
            <label>Prediction Date:</label>
            <span>{new Date(result.timestamp).toLocaleString()}</span>
          </div>
          <div className="info-item">
            <label>Task ID:</label>
            <span className="task-id">{taskId}</span>
          </div>
        </div>
      </div>

      {/* Feature Importance */}
      {featureImportance.length > 0 && (
        <div className="feature-importance">
          <h3>Key Factors Influencing Decision</h3>
          <p>The following factors had the most impact on this prediction:</p>
          
          <div className="importance-list">
            {featureImportance.map((item, index) => (
              <div key={index} className="importance-item">
                <div className="feature-info">
                  <span className="feature-name">{item.feature}</span>
                  <span className="feature-percentage">{item.percentage}%</span>
                </div>
                <div className="importance-bar">
                  <div 
                    className="importance-fill"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Insights */}
      <div className="insights">
        <h3>Additional Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>Model Confidence</h4>
            <p>
              {result.default_probability > 0.8 || result.default_probability < 0.2 
                ? "High confidence in prediction" 
                : "Moderate confidence - consider additional factors"
              }
            </p>
          </div>
          
          <div className="insight-card">
            <h4>Recommendation</h4>
            <p>
              {riskInfo.level === 'Low' && "Approve with standard interest rates"}
              {riskInfo.level === 'Medium' && "Approve with higher interest rates or require collateral"}
              {riskInfo.level === 'High' && "Decline or require significant collateral"}
            </p>
          </div>
          
          <div className="insight-card">
            <h4>Next Steps</h4>
            <p>
              {riskInfo.level === 'Low' && "Process application with standard workflow"}
              {riskInfo.level === 'Medium' && "Conduct manual review and verification"}
              {riskInfo.level === 'High' && "Decline or refer to specialist underwriter"}
            </p>
          </div>
        </div>
      </div>

      {/* Raw Data (for debugging/transparency) */}
      <details className="raw-data">
        <summary>View Raw Prediction Data</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  );
};

export default PredictionResults;
