/**
 * PredictionForm Component
 * Handles credit risk prediction form input and submission
 */

import { useState } from 'react';
import { startPrediction, validatePredictionData } from '../services/api.js';

const PredictionForm = ({ onPredictionStart, onError }) => {
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
    phone_available: '1',
    email_available: '1',
    region_population: '',
    organization_type: 'Business Entity Type 3',
    education_type: 'Higher education',
    income_type: 'Working',
    contract_type: 'Cash loans',
    gender: 'M'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    // Validate required numeric fields
    const numericFields = [
      'external_source_1', 'external_source_2', 'external_source_3',
      'credit_amount', 'annuity_amount', 'goods_price',
      'days_birth', 'days_employed', 'family_size', 'region_population'
    ];

    numericFields.forEach(field => {
      const value = formData[field];
      if (!value || isNaN(value)) {
        errors[field] = `${field.replace(/_/g, ' ')} must be a valid number`;
      }
    });

    // Validate ranges
    if (formData.external_source_1 && (parseFloat(formData.external_source_1) < 0 || parseFloat(formData.external_source_1) > 1)) {
      errors.external_source_1 = 'External source 1 must be between 0 and 1';
    }
    if (formData.external_source_2 && (parseFloat(formData.external_source_2) < 0 || parseFloat(formData.external_source_2) > 1)) {
      errors.external_source_2 = 'External source 2 must be between 0 and 1';
    }
    if (formData.external_source_3 && (parseFloat(formData.external_source_3) < 0 || parseFloat(formData.external_source_3) > 1)) {
      errors.external_source_3 = 'External source 3 must be between 0 and 1';
    }

    if (formData.credit_amount && parseFloat(formData.credit_amount) <= 0) {
      errors.credit_amount = 'Credit amount must be positive';
    }

    if (formData.days_birth && parseFloat(formData.days_birth) >= 0) {
      errors.days_birth = 'Days birth should be negative (days before current date)';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Convert string values to appropriate types
      const predictionData = {
        ...formData,
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
        region_population: parseFloat(formData.region_population)
      };

      // Validate data using API service
      const validation = validatePredictionData(predictionData);
      if (!validation.isValid) {
        setValidationErrors(validation.errors);
        return;
      }

      const response = await startPrediction(predictionData);
      onPredictionStart(response.task_id);
      
    } catch (error) {
      console.error('Prediction submission error:', error);
      onError(error.message || 'Failed to submit prediction request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      external_source_1: '',
      external_source_2: '',
      external_source_3: '',
      credit_amount: '',
      annuity_amount: '',
      goods_price: '',
      days_birth: '',
      days_employed: '',
      family_size: '',
      phone_available: '1',
      email_available: '1',
      region_population: '',
      organization_type: 'Business Entity Type 3',
      education_type: 'Higher education',
      income_type: 'Working',
      contract_type: 'Cash loans',
      gender: 'M'
    });
    setValidationErrors({});
  };

  return (
    <div className="prediction-form">
      <div className="form-header">
        <h2>Credit Risk Prediction</h2>
        <p>Enter applicant information to assess credit risk</p>
      </div>

      <form onSubmit={handleSubmit} className="form-container">
        {/* External Sources */}
        <div className="form-section">
          <h3>External Credit Sources</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="external_source_1">External Source 1 (0-1)</label>
              <input
                type="number"
                id="external_source_1"
                name="external_source_1"
                value={formData.external_source_1}
                onChange={handleInputChange}
                step="0.001"
                min="0"
                max="1"
                className={validationErrors.external_source_1 ? 'error' : ''}
              />
              {validationErrors.external_source_1 && (
                <span className="error-message">{validationErrors.external_source_1}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="external_source_2">External Source 2 (0-1)</label>
              <input
                type="number"
                id="external_source_2"
                name="external_source_2"
                value={formData.external_source_2}
                onChange={handleInputChange}
                step="0.001"
                min="0"
                max="1"
                className={validationErrors.external_source_2 ? 'error' : ''}
              />
              {validationErrors.external_source_2 && (
                <span className="error-message">{validationErrors.external_source_2}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="external_source_3">External Source 3 (0-1)</label>
              <input
                type="number"
                id="external_source_3"
                name="external_source_3"
                value={formData.external_source_3}
                onChange={handleInputChange}
                step="0.001"
                min="0"
                max="1"
                className={validationErrors.external_source_3 ? 'error' : ''}
              />
              {validationErrors.external_source_3 && (
                <span className="error-message">{validationErrors.external_source_3}</span>
              )}
            </div>
          </div>
        </div>

        {/* Financial Information */}
        <div className="form-section">
          <h3>Financial Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="credit_amount">Credit Amount</label>
              <input
                type="number"
                id="credit_amount"
                name="credit_amount"
                value={formData.credit_amount}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                className={validationErrors.credit_amount ? 'error' : ''}
              />
              {validationErrors.credit_amount && (
                <span className="error-message">{validationErrors.credit_amount}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="annuity_amount">Annuity Amount</label>
              <input
                type="number"
                id="annuity_amount"
                name="annuity_amount"
                value={formData.annuity_amount}
                onChange={handleInputChange}
                step="0.01"
                className={validationErrors.annuity_amount ? 'error' : ''}
              />
              {validationErrors.annuity_amount && (
                <span className="error-message">{validationErrors.annuity_amount}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="goods_price">Goods Price</label>
              <input
                type="number"
                id="goods_price"
                name="goods_price"
                value={formData.goods_price}
                onChange={handleInputChange}
                step="0.01"
                className={validationErrors.goods_price ? 'error' : ''}
              />
              {validationErrors.goods_price && (
                <span className="error-message">{validationErrors.goods_price}</span>
              )}
            </div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="form-section">
          <h3>Personal Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="days_birth">Days Birth (negative number)</label>
              <input
                type="number"
                id="days_birth"
                name="days_birth"
                value={formData.days_birth}
                onChange={handleInputChange}
                max="0"
                className={validationErrors.days_birth ? 'error' : ''}
              />
              {validationErrors.days_birth && (
                <span className="error-message">{validationErrors.days_birth}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="days_employed">Days Employed</label>
              <input
                type="number"
                id="days_employed"
                name="days_employed"
                value={formData.days_employed}
                onChange={handleInputChange}
                className={validationErrors.days_employed ? 'error' : ''}
              />
              {validationErrors.days_employed && (
                <span className="error-message">{validationErrors.days_employed}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="family_size">Family Size</label>
              <input
                type="number"
                id="family_size"
                name="family_size"
                value={formData.family_size}
                onChange={handleInputChange}
                min="1"
                className={validationErrors.family_size ? 'error' : ''}
              />
              {validationErrors.family_size && (
                <span className="error-message">{validationErrors.family_size}</span>
              )}
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="gender">Gender</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="phone_available">Phone Available</label>
              <select
                id="phone_available"
                name="phone_available"
                value={formData.phone_available}
                onChange={handleInputChange}
              >
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="email_available">Email Available</label>
              <select
                id="email_available"
                name="email_available"
                value={formData.email_available}
                onChange={handleInputChange}
              >
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
          </div>
        </div>

        {/* Employment and Background */}
        <div className="form-section">
          <h3>Employment & Background</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="income_type">Income Type</label>
              <select
                id="income_type"
                name="income_type"
                value={formData.income_type}
                onChange={handleInputChange}
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
              <select
                id="education_type"
                name="education_type"
                value={formData.education_type}
                onChange={handleInputChange}
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
              <select
                id="organization_type"
                name="organization_type"
                value={formData.organization_type}
                onChange={handleInputChange}
              >
                <option value="Business Entity Type 3">Business Entity Type 3</option>
                <option value="School">School</option>
                <option value="Government">Government</option>
                <option value="Religion">Religion</option>
                <option value="Other">Other</option>
                <option value="XNA">XNA</option>
                <option value="Electricity">Electricity</option>
                <option value="Medicine">Medicine</option>
                <option value="Business Entity Type 2">Business Entity Type 2</option>
                <option value="Self-employed">Self-employed</option>
                <option value="Transport">Transport</option>
                <option value="Construction">Construction</option>
                <option value="Housing">Housing</option>
                <option value="Kindergarten">Kindergarten</option>
                <option value="Trade">Trade</option>
                <option value="Industry">Industry</option>
                <option value="Military">Military</option>
                <option value="Services">Services</option>
                <option value="Security Ministries">Security Ministries</option>
                <option value="Restaurant">Restaurant</option>
                <option value="Culture">Culture</option>
                <option value="Hotel">Hotel</option>
                <option value="Agriculture">Agriculture</option>
                <option value="Police">Police</option>
                <option value="Insurance">Insurance</option>
                <option value="Emergency">Emergency</option>
                <option value="Legal Services">Legal Services</option>
                <option value="Advertising">Advertising</option>
                <option value="Business Entity Type 1">Business Entity Type 1</option>
                <option value="Realtor">Realtor</option>
                <option value="Mobile">Mobile</option>
                <option value="Bank">Bank</option>
                <option value="University">University</option>
                <option value="Postal">Postal</option>
                <option value="Cleaning">Cleaning</option>
                <option value="Telecom">Telecom</option>
                <option value="Security">Security</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="contract_type">Contract Type</label>
              <select
                id="contract_type"
                name="contract_type"
                value={formData.contract_type}
                onChange={handleInputChange}
              >
                <option value="Cash loans">Cash loans</option>
                <option value="Revolving loans">Revolving loans</option>
              </select>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="region_population">Region Population</label>
              <input
                type="number"
                id="region_population"
                name="region_population"
                value={formData.region_population}
                onChange={handleInputChange}
                min="0"
                className={validationErrors.region_population ? 'error' : ''}
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
            onClick={resetForm}
            className="btn btn-secondary"
            disabled={isSubmitting}
          >
            Reset Form
          </button>
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Prediction'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PredictionForm;
