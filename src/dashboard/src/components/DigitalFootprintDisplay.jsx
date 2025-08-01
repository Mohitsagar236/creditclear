import React, { useState, useEffect } from 'react';
import { digitalFootprint } from '../services/digitalFootprint';
import styles from './DigitalFootprintDisplay.module.css';

const DigitalFootprintDisplay = () => {
  const [footprintData, setFootprintData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    const checkConsent = async () => {
      const hasConsent = localStorage.getItem('dataCollectionConsent') === 'true';
      if (hasConsent) {
        collectData();
      } else {
        // Show consent prompt
        const userConsent = window.confirm(
          "To analyze your creditworthiness accurately, we need to collect real device and usage data. " +
          "This helps us build a more accurate profile without requiring extensive paperwork. " +
          "Do you give permission to collect this data from your device? " +
          "No personal files or private information will be accessed."
        );
        
        if (userConsent) {
          localStorage.setItem('dataCollectionConsent', 'true');
          collectData();
        } else {
          setError("You must provide consent to collect device data for a credit assessment. Please refresh and try again.");
        }
      }
    };
    
    checkConsent();
  }, []);

  const collectData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Inform user about data collection
      console.log("Collecting real device data for credit analysis...");
      
      const data = await digitalFootprint.collectDigitalFootprint();
      console.log("Data collection complete:", data);
      
      setFootprintData(data);
      const result = await digitalFootprint.submitFootprintData(data);
      setAnalysisResult(result);
    } catch (err) {
      console.error("Data collection error:", err);
      setError("Failed to collect digital footprint: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="p-8 text-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
      <p className="text-lg">Collecting real device data for credit analysis...</p>
      <p className="text-sm text-gray-500 mt-2">This may take a moment as we gather secure information from your device.</p>
    </div>
  );
  
  if (error) return (
    <div className="p-6 max-w-md mx-auto bg-red-50 border border-red-200 rounded-xl shadow-sm">
      <h3 className="text-lg font-semibold text-red-700 mb-2">Data Collection Error</h3>
      <p className="text-red-600 mb-4">{error}</p>
      <button 
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  );
  
  if (!footprintData) return null;

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Digital Footprint Analysis</h2>
        <button 
          onClick={() => collectData()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Data
        </button>
      </div>
      
      <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-md">
        <div className="flex items-start">
          <div className="mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <p className="font-medium text-green-800">Real Device Data Collection Active</p>
            <p className="text-green-700 text-sm mt-1">
              This assessment is using actual data collected from your device with your permission. No mock or synthetic data is being used.
            </p>
          </div>
        </div>
      </div>
      
      {/* Score and Insights Section */}
      {analysisResult && (
        <div className={`mb-8 ${styles.scoreCard}`}>
          <div className="text-xl font-semibold mb-4">
            Credit Score: {(analysisResult.score * 100).toFixed(1)}
          </div>
          <div className="mb-4">
            <h3 className="font-semibold mb-2">Key Insights:</h3>
            <ul className="list-disc pl-5">
              {analysisResult.insights.map((insight, index) => (
                <li key={index} className="mb-1">{insight}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Recommendations:</h3>
            <ul className="list-disc pl-5">
              {analysisResult.recommendations.map((rec, index) => (
                <li key={index} className="mb-1">{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Digital Identity Section */}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Digital Identity</h3>
        <div className={`grid grid-cols-2 gap-4 bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
          <div>
            <span className="font-medium">Device ID:</span>
            <span className="ml-2">{footprintData.digitalIdentity.deviceId}</span>
          </div>
          <div>
            <span className="font-medium">Account Age:</span>
            <span className="ml-2">{footprintData.digitalIdentity.accountAge} days</span>
          </div>
          <div>
            <span className="font-medium">Email Status:</span>
            <span className={`ml-2 ${styles.tag} ${footprintData.digitalIdentity.emailVerified ? styles.verified : styles.unverified}`}>
              {footprintData.digitalIdentity.emailVerified ? '✅ Verified' : '❌ Not Verified'}
            </span>
          </div>
          <div>
            <span className="font-medium">Phone Status:</span>
            <span className={`ml-2 ${styles.tag} ${footprintData.digitalIdentity.phoneVerified ? styles.verified : styles.unverified}`}>
              {footprintData.digitalIdentity.phoneVerified ? '✅ Verified' : '❌ Not Verified'}
            </span>
          </div>
        </div>
      </section>

      {/* Mobile Usage Section */}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Mobile Usage Patterns</h3>
        <div className={`bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
          <div className="mb-4">
            <h4 className="font-medium mb-2">App Categories</h4>
            <div className="flex flex-wrap gap-2">
              {footprintData.mobileUsage.appCategories.map((category, index) => (
                <span key={index} className={`${styles.tag} bg-blue-100 text-blue-800`}>
                  {category}
                </span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Daily Usage</h4>
              <p>{(footprintData.mobileUsage.usageDuration.daily / 60).toFixed(1)} hours</p>
            </div>
            <div>
              <h4 className="font-medium mb-2">Active Hours</h4>
              <p>{footprintData.mobileUsage.activeHours.join(', ')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Digital Payments Section */}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Digital Payments</h3>
        <div className={`bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Payment Methods</h4>
              <div className="flex flex-wrap gap-2">
                {footprintData.ecommerce.paymentMethods.map((method, index) => (
                  <span key={index} className={`${styles.tag} bg-green-100 text-green-800`}>
                    {method}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Transaction Success Rate</h4>
              <p>{(footprintData.ecommerce.transactionMetrics.successRate * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </section>

      {/* Location Data Section */}
      {footprintData.locationMobility && (
        <section className="mb-6">
          <h3 className="text-xl font-semibold mb-3">Location Patterns</h3>
          <div className={`bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
            <div className="mb-4">
              <h4 className="font-medium mb-2">Frequent Locations</h4>
              <div className="grid grid-cols-1 gap-2">
                {footprintData.locationMobility.frequentLocations.map((location, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="text-sm bg-yellow-100 px-2 py-1 rounded">
                      {location.type}
                    </span>
                    <span className="text-sm">
                      ({location.lat.toFixed(4)}, {location.lng.toFixed(4)})
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Location Stability</h4>
              <div className={`w-full ${styles.progressBar}`}>
                <div
                  className={`bg-blue-600 ${styles.progressFill}`}
                  style={{ width: `${footprintData.locationMobility.locationStability * 100}%` }}
                />
              </div>
              <p className="text-sm mt-1">
                {(footprintData.locationMobility.locationStability * 100).toFixed(1)}% stable
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Device Technical Section */}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Device Information</h3>
        <div className={`bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Device Details</h4>
              <p className="text-sm">OS: {footprintData.deviceTechnical.device.os}</p>
              <p className="text-sm">Language: {footprintData.deviceTechnical.device.language}</p>
            </div>
            <div>
              <h4 className="font-medium mb-2">Security Score</h4>
              <div className={`w-full ${styles.progressBar}`}>
                <div
                  className={`bg-green-600 ${styles.progressFill}`}
                  style={{ width: `${footprintData.deviceTechnical.security.score * 100}%` }}
                />
              </div>
              <p className="text-sm mt-1">
                {(footprintData.deviceTechnical.security.score * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Utility Services Section */}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Utility Services</h3>
        <div className={`bg-white p-4 rounded-lg shadow ${styles.dataSection}`}>
          <div className="mb-4">
            <h4 className="font-medium mb-2">Active Subscriptions</h4>
            <div className="flex flex-wrap gap-2">
              {footprintData.utilityServices.subscriptions.map((sub, index) => (
                <span key={index} className={`${styles.tag} bg-purple-100 text-purple-800`}>
                  {sub}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-2">Payment Consistency</h4>
            <div className={`w-full ${styles.progressBar}`}>
              <div
                className={`bg-purple-600 ${styles.progressFill}`}
                style={{ width: `${footprintData.utilityServices.paymentConsistency * 100}%` }}
              />
            </div>
            <p className="text-sm mt-1">
              {(footprintData.utilityServices.paymentConsistency * 100).toFixed(1)}% consistent
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DigitalFootprintDisplay;
