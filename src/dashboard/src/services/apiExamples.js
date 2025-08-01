/**
 * Example usage of the API service functions.
 * This file demonstrates how to use the API service in React components.
 */

import { useState } from 'react';
import { 
  startPrediction, 
  getPredictionResult, 
  pollPredictionResult, 
  checkApiHealth,
  validatePredictionData 
} from './api.js';

// Example prediction data
const examplePredictionData = {
  AMT_INCOME_TOTAL: 202500.0,
  AMT_CREDIT: 406597.5,
  AMT_ANNUITY: 24700.5,
  AMT_GOODS_PRICE: 351000.0,
  NAME_CONTRACT_TYPE: "Cash loans",
  CODE_GENDER: "M",
  FLAG_OWN_CAR: "N",
  FLAG_OWN_REALTY: "Y",
  CNT_CHILDREN: 0,
  NAME_EDUCATION_TYPE: "Higher education",
  DAYS_BIRTH: -9461,
  DAYS_EMPLOYED: -637,
  EXT_SOURCE_1: 0.083037,
  EXT_SOURCE_2: 0.262949,
  EXT_SOURCE_3: 0.139376,
  REGION_POPULATION_RELATIVE: 0.018801,
  HOUR_APPR_PROCESS_START: 10
};

/**
 * Example: Complete prediction workflow
 */
export const examplePredictionWorkflow = async () => {
  try {
    console.log('🔍 Validating prediction data...');
    
    // Step 1: Validate the data
    const validation = validatePredictionData(examplePredictionData);
    if (!validation.isValid) {
      console.error('❌ Validation failed:', validation.errors);
      return;
    }
    
    console.log('✅ Data validation passed');
    
    // Step 2: Check API health
    console.log('🏥 Checking API health...');
    const health = await checkApiHealth();
    console.log('Health status:', health);
    
    if (!health.success) {
      console.error('❌ API is not healthy');
      return;
    }
    
    // Step 3: Start prediction
    console.log('🚀 Starting prediction...');
    const predictionResponse = await startPrediction(examplePredictionData);
    console.log('Prediction started:', predictionResponse);
    
    const taskId = predictionResponse.taskId;
    
    // Step 4: Poll for results
    console.log('⏳ Polling for results...');
    const result = await pollPredictionResult(taskId, {
      maxAttempts: 30,
      interval: 2000,
      onProgress: (progress, attempt) => {
        console.log(`📊 Attempt ${attempt}: Status = ${progress.status}`);
      }
    });
    
    console.log('🎉 Final result:', result);
    
    if (result.status === 'completed' && result.result) {
      const { predictionProbability, riskCategory, confidenceScore } = result.result;
      console.log(`📈 Risk Probability: ${(predictionProbability * 100).toFixed(2)}%`);
      console.log(`🏷️  Risk Category: ${riskCategory}`);
      console.log(`🎯 Confidence: ${(confidenceScore * 100).toFixed(2)}%`);
    }
    
    return result;
    
  } catch (error) {
    console.error('❌ Prediction workflow failed:', error.message);
    throw error;
  }
};

/**
 * Example: Manual step-by-step prediction
 */
export const exampleManualPrediction = async () => {
  try {
    // Start prediction
    const prediction = await startPrediction(examplePredictionData);
    console.log('Prediction started with task ID:', prediction.taskId);
    
    // Wait a bit
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check result manually
    const result = await getPredictionResult(prediction.taskId);
    console.log('Current status:', result.status);
    
    if (result.status === 'completed') {
      console.log('Prediction result:', result.result);
    } else if (result.status === 'failed') {
      console.error('Prediction failed:', result.error);
    } else {
      console.log('Prediction still processing...');
    }
    
    return result;
    
  } catch (error) {
    console.error('Manual prediction failed:', error);
    throw error;
  }
};

/**
 * Example: React Hook for using the API
 */
export const usePredictionExample = () => {
  // This would be used in a React component
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const submitPrediction = async (data) => {
    setLoading(true);
    setError(null);
    
    try {
      // Validate data
      const validation = validatePredictionData(data);
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
      }
      
      // Start prediction
      const prediction = await startPrediction(data);
      
      // Poll for results
      const finalResult = await pollPredictionResult(prediction.taskId, {
        onProgress: (progress) => {
          // Update UI with progress
          console.log('Progress:', progress.status);
        }
      });
      
      setResult(finalResult);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return { loading, result, error, submitPrediction };
};
