import React, { useState, useEffect } from 'react';
import { digitalFootprint } from '../services/digitalFootprint';
import './DigitalFootprintDisplay.css';

const DigitalFootprintDisplay = () => {
  const [footprintData, setFootprintData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    collectData();
  }, []);

  const collectData = async () => {
    try {
      setLoading(true);
      const data = await digitalFootprint.collectDigitalFootprint();
      setFootprintData(data);
      const result = await digitalFootprint.submitFootprintData();
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-state">Collecting digital footprint data...</div>;
  if (error) return <div className="error-state">Error: {error}</div>;
  if (!footprintData) return null;

  return (
    <div className="digital-footprint-container">
      <h2 className="section-title" style={{fontSize: '1.5rem', marginBottom: '1.5rem'}}>Digital Footprint Analysis</h2>
      
      {/* Score and Insights Section */}
      {analysisResult && (
        <div className="score-card">
          <div style={{fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem'}}>
            Credit Score: {(analysisResult.score * 100).toFixed(1)}
          </div>
          <div style={{marginBottom: '1rem'}}>
            <h3 className="subsection-title" style={{color: 'white'}}>Key Insights:</h3>
            <ul style={{listStyle: 'disc', paddingLeft: '1.25rem'}}>
              {analysisResult.insights.map((insight, index) => (
                <li key={index} style={{marginBottom: '0.25rem'}}>{insight}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="subsection-title" style={{color: 'white'}}>Recommendations:</h3>
            <ul style={{listStyle: 'disc', paddingLeft: '1.25rem'}}>
              {analysisResult.recommendations.map((rec, index) => (
                <li key={index} style={{marginBottom: '0.25rem'}}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Digital Identity Section */}
      <section>
        <h3 className="section-title">Digital Identity</h3>
        <div className="data-section">
          <div className="grid-2">
            <div>
              <span style={{fontWeight: '500'}}>Device ID:</span>
              <span style={{marginLeft: '0.5rem'}}>{footprintData.digitalIdentity.deviceId}</span>
            </div>
            <div>
              <span style={{fontWeight: '500'}}>Account Age:</span>
              <span style={{marginLeft: '0.5rem'}}>{footprintData.digitalIdentity.accountAge} days</span>
            </div>
            <div>
              <span style={{fontWeight: '500'}}>Email Status:</span>
              <span className={footprintData.digitalIdentity.emailVerified ? 'verified-status' : 'unverified-status'} style={{marginLeft: '0.5rem'}}>
                {footprintData.digitalIdentity.emailVerified ? '✅ Verified' : '❌ Not Verified'}
              </span>
            </div>
            <div>
              <span style={{fontWeight: '500'}}>Phone Status:</span>
              <span className={footprintData.digitalIdentity.phoneVerified ? 'verified-status' : 'unverified-status'} style={{marginLeft: '0.5rem'}}>
                {footprintData.digitalIdentity.phoneVerified ? '✅ Verified' : '❌ Not Verified'}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Mobile Usage Section */}
      <section>
        <h3 className="section-title">Mobile Usage Patterns</h3>
        <div className="data-section">
          <div style={{marginBottom: '1rem'}}>
            <h4 className="subsection-title">App Categories</h4>
            <div className="flex-wrap">
              {footprintData.mobileUsage.appCategories.map((category, index) => (
                <span key={index} className="data-tag" style={{backgroundColor: '#dbeafe', color: '#1e40af'}}>
                  {category}
                </span>
              ))}
            </div>
          </div>
          <div className="grid-2">
            <div>
              <h4 className="subsection-title">Daily Usage</h4>
              <p>{(footprintData.mobileUsage.usageDuration.daily / 60).toFixed(1)} hours</p>
            </div>
            <div>
              <h4 className="subsection-title">Active Hours</h4>
              <p>{footprintData.mobileUsage.activeHours.join(', ')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Digital Payments Section */}
      <section>
        <h3 className="section-title">Digital Payments</h3>
        <div className="data-section">
          <div className="grid-2">
            <div>
              <h4 className="subsection-title">Payment Methods</h4>
              <div className="flex-wrap">
                {footprintData.ecommerce.paymentMethods.map((method, index) => (
                  <span key={index} className="data-tag" style={{backgroundColor: '#dcfce7', color: '#166534'}}>
                    {method}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="subsection-title">Transaction Success Rate</h4>
              <p>{(footprintData.ecommerce.transactionMetrics.successRate * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </section>

      {/* Location Data Section */}
      {footprintData.locationMobility && (
        <section>
          <h3 className="section-title">Location Patterns</h3>
          <div className="data-section">
            <div style={{marginBottom: '1rem'}}>
              <h4 className="subsection-title">Frequent Locations</h4>
              <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                {footprintData.locationMobility.frequentLocations.map((location, index) => (
                  <div key={index} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                    <span className="data-tag" style={{backgroundColor: '#fef3c7', color: '#92400e'}}>
                      {location.type}
                    </span>
                    <span style={{fontSize: '0.875rem'}}>
                      ({location.lat.toFixed(4)}, {location.lng.toFixed(4)})
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="subsection-title">Location Stability</h4>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ 
                    width: `${footprintData.locationMobility.locationStability * 100}%`,
                    backgroundColor: '#3b82f6'
                  }}
                />
              </div>
              <p style={{fontSize: '0.875rem', marginTop: '0.25rem'}}>
                {(footprintData.locationMobility.locationStability * 100).toFixed(1)}% stable
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Device Technical Section */}
      <section>
        <h3 className="section-title">Device Information</h3>
        <div className="data-section">
          <div className="grid-2">
            <div>
              <h4 className="subsection-title">Device Details</h4>
              <p style={{fontSize: '0.875rem'}}>OS: {footprintData.deviceTechnical.device.os}</p>
              <p style={{fontSize: '0.875rem'}}>Language: {footprintData.deviceTechnical.device.language}</p>
            </div>
            <div>
              <h4 className="subsection-title">Security Score</h4>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ 
                    width: `${footprintData.deviceTechnical.security.score * 100}%`,
                    backgroundColor: '#10b981'
                  }}
                />
              </div>
              <p style={{fontSize: '0.875rem', marginTop: '0.25rem'}}>
                {(footprintData.deviceTechnical.security.score * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Utility Services Section */}
      <section>
        <h3 className="section-title">Utility Services</h3>
        <div className="data-section">
          <div style={{marginBottom: '1rem'}}>
            <h4 className="subsection-title">Active Subscriptions</h4>
            <div className="flex-wrap">
              {footprintData.utilityServices.subscriptions.map((sub, index) => (
                <span key={index} className="data-tag" style={{backgroundColor: '#e9d5ff', color: '#7c3aed'}}>
                  {sub}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h4 className="subsection-title">Payment Consistency</h4>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ 
                  width: `${footprintData.utilityServices.paymentConsistency * 100}%`,
                  backgroundColor: '#8b5cf6'
                }}
              />
            </div>
            <p style={{fontSize: '0.875rem', marginTop: '0.25rem'}}>
              {(footprintData.utilityServices.paymentConsistency * 100).toFixed(1)}% consistent
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DigitalFootprintDisplay;
