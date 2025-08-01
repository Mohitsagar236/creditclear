/**
 * Dashboard Component - Main page for credit risk prediction
 * 
 * This component provides:
 * 1. A form with input fields corresponding to the PredictionRequest schema
 * 2. A submit button that calls the startPrediction service function
 * 3. State management using useState to store form data, task ID, and prediction result
 * 4. A display area to show the prediction result once fetched using getPredictionResult
 */

import React, { useState, useEffect } from 'react';
import { 
  startPrediction, 
  pollPredictionResult,
  checkApiHealth,
  validatePredictionData 
} from '../src/services/api.js';

const Dashboard = () => {
  // Form data state matching PredictionRequest schema
  const [formData, setFormData] = useState({
    external_source_1: '',
    external_source_2: '',
    external_source_3: '',
    credit_amount: '',
    annuity_amount: '',
    goods_price: '',
    days_birth: '',
    days_employed: '',
    family_size: '',
    phone_available: 1,
    email_available: 1,
    region_population: '',
    organization_type: 'Business Entity Type 3',
    education_type: 'Higher education',
    income_type: 'Working',
    contract_type: 'Cash loans',
    gender: 'M'
  });

  // Application state
  const [taskId, setTaskId] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [apiHealth, setApiHealth] = useState('checking');

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await checkApiHealth();
        setApiHealth('connected');
      } catch {
        setApiHealth('disconnected');
        setError('Unable to connect to API server. Please ensure the backend is running.');
      }
    };
    checkHealth();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    const processedValue = type === 'number' ? parseFloat(value) || '' : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: processedValue
    }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  // Validate form data
  const validateForm = () => {
    const errors = {};
    
    // Required numeric fields validation
    const numericFields = [
      'external_source_1', 'external_source_2', 'external_source_3',
      'credit_amount', 'annuity_amount', 'goods_price',
      'days_birth', 'days_employed', 'family_size', 'region_population'
    ];

    numericFields.forEach(field => {
      const value = formData[field];
      if (value === '' || isNaN(value)) {
        errors[field] = `${field.replace(/_/g, ' ')} is required and must be a valid number`;
      }
    });

    // Range validations
    ['external_source_1', 'external_source_2', 'external_source_3'].forEach(field => {
      const value = parseFloat(formData[field]);
      if (!isNaN(value) && (value < 0 || value > 1)) {
        errors[field] = `${field.replace(/_/g, ' ')} must be between 0 and 1`;
      }
    });

    if (formData.credit_amount && parseFloat(formData.credit_amount) <= 0) {
      errors.credit_amount = 'Credit amount must be positive';
    }

    if (formData.days_birth && parseFloat(formData.days_birth) >= 0) {
      errors.days_birth = 'Days birth should be negative (days before current date)';
    }

    if (formData.family_size && parseFloat(formData.family_size) < 1) {
      errors.family_size = 'Family size must be at least 1';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setError('Please fix the validation errors before submitting');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Convert form data to proper types for API
      const predictionData = {
        external_source_1: parseFloat(formData.external_source_1),
        external_source_2: parseFloat(formData.external_source_2),
        external_source_3: parseFloat(formData.external_source_3),
        credit_amount: parseFloat(formData.credit_amount),
        annuity_amount: parseFloat(formData.annuity_amount),
        goods_price: parseFloat(formData.goods_price),
        days_birth: parseInt(formData.days_birth),
        days_employed: parseInt(formData.days_employed),
        family_size: parseInt(formData.family_size),
        phone_available: parseInt(formData.phone_available),
        email_available: parseInt(formData.email_available),
        region_population: parseFloat(formData.region_population),
        organization_type: formData.organization_type,
        education_type: formData.education_type,
        income_type: formData.income_type,
        contract_type: formData.contract_type,
        gender: formData.gender
      };

      // Validate data using API service
      const validation = validatePredictionData(predictionData);
      if (!validation.isValid) {
        setValidationErrors(validation.errors);
        setError('Please fix the validation errors');
        return;
      }

      // Submit prediction request
      const response = await startPrediction(predictionData);
      setTaskId(response.task_id);
      
      // Start polling for results
      setIsLoading(true);
      await pollForResults(response.task_id);

    } catch (err) {
      console.error('Prediction submission error:', err);
      setError(err.message || 'Failed to submit prediction request');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Poll for prediction results
  const pollForResults = async (id) => {
    try {
      const result = await pollPredictionResult(id, {
        maxAttempts: 30,
        intervalMs: 2000,
        onProgress: (attempt, maxAttempts) => {
          console.log(`Polling attempt ${attempt}/${maxAttempts}`);
        }
      });
      
      setPredictionResult(result);
      setIsLoading(false);
      
    } catch (err) {
      console.error('Error polling for results:', err);
      setError(err.message || 'Failed to get prediction results');
      setIsLoading(false);
    }
  };

  // Reset form and start new prediction
  const startNewPrediction = () => {
    setTaskId(null);
    setPredictionResult(null);
    setError(null);
    setIsLoading(false);
    setValidationErrors({});
  };

  // Get risk level styling
  const getRiskLevel = (probability) => {
    if (probability < 0.3) return { level: 'Low', class: 'risk-low', color: '#28a745' };
    if (probability < 0.7) return { level: 'Medium', class: 'risk-medium', color: '#ffc107' };
    return { level: 'High', class: 'risk-high', color: '#dc3545' };
  };

  // Format feature importance for display
  const formatFeatureImportance = (features) => {
    if (!features || typeof features !== 'object') return [];
    
    return Object.entries(features)
      .map(([feature, importance]) => ({
        feature: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        importance: parseFloat(importance),
        percentage: (parseFloat(importance) * 100).toFixed(1)
      }))
      .sort((a, b) => b.importance - a.importance)
      .slice(0, 10);
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="title-section">
            <h1>Credit Risk Assessment System</h1>
            <p>AI-powered credit risk evaluation and decision support</p>
          </div>
          
          <div className="status-section">
            <div className={`api-status status-${apiHealth}`}>
              <div className="status-indicator"></div>
              <span>API {apiHealth === 'connected' ? 'Connected' : apiHealth === 'disconnected' ? 'Disconnected' : 'Checking...'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="dashboard-main">
        {apiHealth === 'disconnected' ? (
          // Connection Error State
          <div className="connection-error">
            <div className="error-icon">🔌</div>
            <h2>Connection Required</h2>
            <p>Please ensure the backend API server is running and accessible.</p>
            <div className="connection-help">
              <h4>To start the backend server:</h4>
              <pre>uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000</pre>
            </div>
          </div>
        ) : predictionResult ? (
          // Results Display Area
          <div className="prediction-results">
            <div className="results-header">
              <h2>Credit Risk Assessment Results</h2>
              <button onClick={startNewPrediction} className="btn btn-outline">
                New Prediction
              </button>
            </div>

            {/* Risk Score Display */}
            <div className="risk-score-container">
              {(() => {
                const riskInfo = getRiskLevel(predictionResult.default_probability);
                return (
                  <div className={`risk-score ${riskInfo.class}`}>
                    <div className="risk-level">
                      <span className="level-text">{riskInfo.level} Risk</span>
                      <span className="probability-text">
                        {(predictionResult.default_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="risk-meter">
                      <div 
                        className="risk-fill"
                        style={{ 
                          width: `${predictionResult.default_probability * 100}%`,
                          backgroundColor: riskInfo.color 
                        }}
                      ></div>
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
                );
              })()}
            </div>

            {/* Model Information */}
            <div className="model-info">
              <div className="info-row">
                <div className="info-item">
                  <label>Model Used:</label>
                  <span>{predictionResult.model_version || 'XGBoost v1.0'}</span>
                </div>
                <div className="info-item">
                  <label>Prediction Date:</label>
                  <span>{new Date(predictionResult.timestamp || Date.now()).toLocaleString()}</span>
                </div>
                <div className="info-item">
                  <label>Task ID:</label>
                  <span className="task-id">{taskId}</span>
                </div>
              </div>
            </div>

            {/* Feature Importance */}
            {predictionResult.feature_importance && (
              <div className="feature-importance">
                <h3>Key Factors Influencing Decision</h3>
                <p>The following factors had the most impact on this prediction:</p>
                
                <div className="importance-list">
                  {formatFeatureImportance(predictionResult.feature_importance).map((item, index) => (
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

            {/* Raw Data for Debugging */}
            <details className="raw-data">
              <summary>View Raw Prediction Data</summary>
              <pre>{JSON.stringify(predictionResult, null, 2)}</pre>
            </details>
          </div>
        ) : isLoading ? (
          // Loading State
          <div className="loading">
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Processing prediction...</p>
              <small>This may take a few moments</small>
              {taskId && <p className="task-id">Task ID: {taskId}</p>}
            </div>
          </div>
        ) : (
          // Prediction Form
          <div className="prediction-form">
            <div className="form-header">
              <h2>Credit Risk Prediction</h2>
              <p>Enter applicant information to assess credit risk</p>
            </div>

            <form onSubmit={handleSubmit} className="form-container">
              {/* External Sources Section */}
              <div className="form-section">
                <h3>External Credit Sources</h3>
                <p className="section-description">
                  Normalized credit scores from external agencies (e.g., credit bureaus, financial institutions). 
                  Values are normalized between 0-1, where higher values indicate better creditworthiness.
                </p>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="external_source_1">External Source 1 - Credit Bureau Score (0-1)</label>
                    <small className="field-help">Primary credit bureau score (normalized)</small>
                    <input
                      type="number"
                      id="external_source_1"
                      name="external_source_1"
                      value={formData.external_source_1}
                      onChange={handleInputChange}
                      step="0.001"
                      min="0"
                      max="1"
                      placeholder="e.g., 0.725"
                      className={validationErrors.external_source_1 ? 'error' : ''}
                      required
                    />
                    {validationErrors.external_source_1 && (
                      <span className="error-message">{validationErrors.external_source_1}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="external_source_2">External Source 2 - Banking History Score (0-1)</label>
                    <small className="field-help">Banking relationship and transaction history score</small>
                    <input
                      type="number"
                      id="external_source_2"
                      name="external_source_2"
                      value={formData.external_source_2}
                      onChange={handleInputChange}
                      step="0.001"
                      min="0"
                      max="1"
                      placeholder="e.g., 0.542"
                      className={validationErrors.external_source_2 ? 'error' : ''}
                      required
                    />
                    {validationErrors.external_source_2 && (
                      <span className="error-message">{validationErrors.external_source_2}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="external_source_3">External Source 3 - Alternative Data Score (0-1)</label>
                    <small className="field-help">Alternative data sources (telecom, utilities, retail history)</small>
                    <input
                      type="number"
                      id="external_source_3"
                      name="external_source_3"
                      value={formData.external_source_3}
                      onChange={handleInputChange}
                      step="0.001"
                      min="0"
                      max="1"
                      placeholder="e.g., 0.631"
                      className={validationErrors.external_source_3 ? 'error' : ''}
                      required
                    />
                    {validationErrors.external_source_3 && (
                      <span className="error-message">{validationErrors.external_source_3}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Financial Information Section */}
              <div className="form-section">
                <h3>Financial Information</h3>
                <p className="section-description">
                  Key financial details about the loan and associated costs.
                </p>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="credit_amount">Credit Amount</label>
                    <small className="field-help">Total loan amount requested by the applicant</small>
                    <input
                      type="number"
                      id="credit_amount"
                      name="credit_amount"
                      value={formData.credit_amount}
                      onChange={handleInputChange}
                      step="0.01"
                      min="0"
                      placeholder="e.g., 50000"
                      className={validationErrors.credit_amount ? 'error' : ''}
                      required
                    />
                    {validationErrors.credit_amount && (
                      <span className="error-message">{validationErrors.credit_amount}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="annuity_amount">Annuity Amount</label>
                    <small className="field-help">Monthly payment amount (loan payment per period)</small>
                    <input
                      type="number"
                      id="annuity_amount"
                      name="annuity_amount"
                      value={formData.annuity_amount}
                      onChange={handleInputChange}
                      step="0.01"
                      placeholder="e.g., 3500"
                      className={validationErrors.annuity_amount ? 'error' : ''}
                      required
                    />
                    {validationErrors.annuity_amount && (
                      <span className="error-message">{validationErrors.annuity_amount}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="goods_price">Goods Price</label>
                    <small className="field-help">Price of goods/services the loan is for (if applicable)</small>
                    <input
                      type="number"
                      id="goods_price"
                      name="goods_price"
                      value={formData.goods_price}
                      onChange={handleInputChange}
                      step="0.01"
                      placeholder="e.g., 48000"
                      className={validationErrors.goods_price ? 'error' : ''}
                      required
                    />
                    {validationErrors.goods_price && (
                      <span className="error-message">{validationErrors.goods_price}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Personal Information Section */}
              <div className="form-section">
                <h3>Personal Information</h3>
                <p className="section-description">
                  Personal demographics and life circumstances that affect creditworthiness.
                </p>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="days_birth">Days Birth (negative number)</label>
                    <small className="field-help">Age in days as negative number (e.g., -15000 for ~41 years old)</small>
                    <input
                      type="number"
                      id="days_birth"
                      name="days_birth"
                      value={formData.days_birth}
                      onChange={handleInputChange}
                      max="0"
                      placeholder="e.g., -15000"
                      className={validationErrors.days_birth ? 'error' : ''}
                      required
                    />
                    {validationErrors.days_birth && (
                      <span className="error-message">{validationErrors.days_birth}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="days_employed">Days Employed</label>
                    <small className="field-help">Employment duration in days (negative for unemployed period)</small>
                    <input
                      type="number"
                      id="days_employed"
                      name="days_employed"
                      value={formData.days_employed}
                      onChange={handleInputChange}
                      placeholder="e.g., -1200"
                      className={validationErrors.days_employed ? 'error' : ''}
                      required
                    />
                    {validationErrors.days_employed && (
                      <span className="error-message">{validationErrors.days_employed}</span>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="family_size">Family Size</label>
                    <small className="field-help">Total number of family members including applicant</small>
                    <input
                      type="number"
                      id="family_size"
                      name="family_size"
                      value={formData.family_size}
                      onChange={handleInputChange}
                      min="1"
                      placeholder="e.g., 3"
                      className={validationErrors.family_size ? 'error' : ''}
                      required
                    />
                    {validationErrors.family_size && (
                      <span className="error-message">{validationErrors.family_size}</span>
                    )}
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="gender">Gender</label>
                    <small className="field-help">Applicant's gender (demographic factor)</small>
                    <select
                      id="gender"
                      name="gender"
                      value={formData.gender}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="phone_available">Phone Available</label>
                    <small className="field-help">Whether applicant has provided a contact phone number</small>
                    <select
                      id="phone_available"
                      name="phone_available"
                      value={formData.phone_available}
                      onChange={handleInputChange}
                      required
                    >
                      <option value={1}>Yes</option>
                      <option value={0}>No</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="email_available">Email Available</label>
                    <small className="field-help">Whether applicant has provided a contact email address</small>
                    <select
                      id="email_available"
                      name="email_available"
                      value={formData.email_available}
                      onChange={handleInputChange}
                      required
                    >
                      <option value={1}>Yes</option>
                      <option value={0}>No</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Employment and Background Section */}
              <div className="form-section">
                <h3>Employment & Background</h3>
                <p className="section-description">
                  Professional background and socioeconomic factors that influence credit risk assessment.
                </p>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="income_type">Income Type</label>
                    <small className="field-help">Primary source of applicant's income</small>
                    <select
                      id="income_type"
                      name="income_type"
                      value={formData.income_type}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="Working">Working</option>
                      <option value="Commercial associate">Commercial associate</option>
                      <option value="Pensioner">Pensioner</option>
                      <option value="State servant">State servant</option>
                      <option value="Student">Student</option>
                      <option value="Businessman">Businessman</option>
                      <option value="Maternity leave">Maternity leave</option>
                      <option value="Unemployed">Unemployed</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="education_type">Education Type</label>
                    <small className="field-help">Highest level of education completed</small>
                    <select
                      id="education_type"
                      name="education_type"
                      value={formData.education_type}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="Higher education">Higher education</option>
                      <option value="Secondary / secondary special">Secondary / secondary special</option>
                      <option value="Incomplete higher">Incomplete higher</option>
                      <option value="Lower secondary">Lower secondary</option>
                      <option value="Academic degree">Academic degree</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="organization_type">Organization Type</label>
                    <small className="field-help">Type of organization where applicant works</small>
                    <select
                      id="organization_type"
                      name="organization_type"
                      value={formData.organization_type}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="Business Entity Type 3">Business Entity Type 3</option>
                      <option value="School">School</option>
                      <option value="Government">Government</option>
                      <option value="Religion">Religion</option>
                      <option value="Other">Other</option>
                      <option value="XNA">XNA</option>
                      <option value="Self-employed">Self-employed</option>
                      <option value="Industry">Industry</option>
                      <option value="Medicine">Medicine</option>
                      <option value="Trade">Trade</option>
                      <option value="Construction">Construction</option>
                      <option value="Transport">Transport</option>
                      <option value="Military">Military</option>
                      <option value="Police">Police</option>
                      <option value="Bank">Bank</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="contract_type">Contract Type</label>
                    <small className="field-help">Type of loan contract being applied for</small>
                    <select
                      id="contract_type"
                      name="contract_type"
                      value={formData.contract_type}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="Cash loans">Cash loans</option>
                      <option value="Revolving loans">Revolving loans</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="region_population">Region Population</label>
                    <small className="field-help">Population of the region where applicant lives (demographic factor)</small>
                    <input
                      type="number"
                      id="region_population"
                      name="region_population"
                      value={formData.region_population}
                      onChange={handleInputChange}
                      min="0"
                      placeholder="e.g., 500000"
                      className={validationErrors.region_population ? 'error' : ''}
                      required
                    />
                    {validationErrors.region_population && (
                      <span className="error-message">{validationErrors.region_population}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Form Actions */}
              <div className="form-actions">
                <button
                  type="button"
                  onClick={startNewPrediction}
                  className="btn btn-secondary"
                  disabled={isSubmitting}
                >
                  Reset Form
                </button>
                
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting || apiHealth !== 'connected'}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Prediction'}
                </button>
              </div>
            </form>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="dashboard-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>About</h4>
            <p>
              This system uses advanced machine learning algorithms including XGBoost and LightGBM 
              to assess credit risk based on applicant data and external credit scores.
            </p>
          </div>
          
          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li>Real-time risk assessment</li>
              <li>Feature importance analysis</li>
              <li>Model explainability</li>
              <li>Automated decision support</li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Models</h4>
            <ul>
              <li>XGBoost Classifier</li>
              <li>LightGBM Classifier</li>
              <li>Feature Engineering Pipeline</li>
              <li>SHAP Explainability</li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 Credit Risk Assessment System. Built with React, FastAPI, and ML.</p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
