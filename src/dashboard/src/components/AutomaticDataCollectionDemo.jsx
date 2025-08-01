import React, { useState, useEffect } from 'react';

const AutomaticDataCollectionDemo = () => {
  const [loading, setLoading] = useState(false);
  const [consentGranted, setConsentGranted] = useState(false);
  const [collectionStatus, setCollectionStatus] = useState('idle');
  const [collectedData, setCollectedData] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkExistingConsent();
  }, []);

  const checkExistingConsent = async () => {
    try {
      const hasExistingConsent = localStorage.getItem('dataCollectionConsent') === 'true';
      setConsentGranted(hasExistingConsent);
      
      if (hasExistingConsent) {
        const cachedData = localStorage.getItem('cachedComprehensiveData');
        if (cachedData) {
          setCollectedData(JSON.parse(cachedData));
        }
      }
    } catch (err) {
      console.error('Error checking consent:', err);
    }
  };

  const requestConsent = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const consent = window.confirm(`🔒 Comprehensive Data Collection Consent

We'd like to automatically collect data to provide better credit assessment:

• 📱 Device information and specifications
• 🌍 Location patterns (anonymized)  
• 💳 Digital footprint analysis
• ⚡ Utility and service patterns
• 📊 Usage analytics

All data is encrypted and used only for risk assessment.

Grant consent for automatic data collection?`);
      
      if (consent) {
        setConsentGranted(true);
        localStorage.setItem('dataCollectionConsent', 'true');
        await startDataCollection();
      } else {
        setError('Consent denied. Manual data entry will be required.');
      }
    } catch (err) {
      setError(`Consent error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const startDataCollection = async () => {
    try {
      setLoading(true);
      setCollectionStatus('collecting');
      setError(null);

      const phases = [
        'Detecting device capabilities...',
        'Analyzing digital footprint...',
        'Collecting location patterns...',
        'Processing utility data...',
        'Generating risk assessment...'
      ];

      for (let i = 0; i < phases.length; i++) {
        setCollectionStatus(phases[i]);
        await new Promise(resolve => setTimeout(resolve, 1500));
      }

      const mockData = {
        device: {
          type: 'desktop',
          os: navigator.platform,
          browser: 'Chrome',
          screenResolution: `${screen.width}x${screen.height}`,
          language: navigator.language,
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
        },
        digitalFootprint: {
          onlinePresence: 'moderate',
          socialMediaActivity: 'active',
          eCommerceHistory: 'regular',
          financialAppsUsage: 'frequent'
        },
        location: {
          currentCity: 'Mumbai',
          homeLocation: 'detected',
          workLocation: 'detected',
          travelPatterns: 'regular_commuter'
        },
        utility: {
          mobileRecharge: 'regular',
          electricityBill: 'consistent',
          internetUsage: 'high',
          subscriptionServices: 'multiple'
        }
      };

      setCollectedData(mockData);
      localStorage.setItem('cachedComprehensiveData', JSON.stringify(mockData));

      const assessment = {
        overallScore: 742,
        riskLevel: 'Low-Medium',
        confidence: 0.87,
        factors: {
          deviceStability: 0.85,
          digitalFootprint: 0.90,
          locationConsistency: 0.88,
          utilityPatterns: 0.82
        },
        recommendations: [
          'Strong digital presence indicates financial stability',
          'Regular utility payments show responsibility',
          'Consistent location patterns reduce fraud risk'
        ]
      };

      setRiskAssessment(assessment);
      setCollectionStatus('complete');
    } catch (err) {
      setError(`Collection error: ${err.message}`);
      setCollectionStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const revokeConsent = () => {
    if (window.confirm('Are you sure you want to revoke data collection consent?')) {
      setConsentGranted(false);
      setCollectedData(null);
      setRiskAssessment(null);
      setCollectionStatus('idle');
      localStorage.removeItem('dataCollectionConsent');
      localStorage.removeItem('cachedComprehensiveData');
    }
  };

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h2 style={{ 
          color: 'var(--text-primary, #1a1a1a)', 
          fontSize: '2rem', 
          marginBottom: '0.5rem' 
        }}>
          🤖 Smart Data Collection
        </h2>
        <p style={{ 
          color: 'var(--text-secondary, #666)', 
          fontSize: '1.1rem' 
        }}>
          Comprehensive automatic data gathering for enhanced credit assessment
        </p>
      </div>

      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #ef4444',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '2rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: '#ef4444'
        }}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {!consentGranted ? (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '3rem 0' }}>
          <div style={{
            backgroundColor: 'var(--bg-primary, #fff)',
            border: '2px solid var(--border-color, #e5e5e5)',
            borderRadius: '16px',
            padding: '3rem',
            textAlign: 'center',
            maxWidth: '600px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ marginBottom: '2rem' }}>
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔒</div>
              <h3 style={{ color: 'var(--text-primary, #1a1a1a)', marginBottom: '1rem' }}>
                Data Collection Consent Required
              </h3>
              <p style={{ color: 'var(--text-secondary, #666)', lineHeight: '1.6' }}>
                Enable automatic data collection to streamline the credit assessment process.
              </p>
            </div>
            
            <div style={{ marginBottom: '2rem', textAlign: 'left' }}>
              <h4 style={{ color: 'var(--text-primary, #1a1a1a)', marginBottom: '1rem' }}>
                Data Sources:
              </h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '1rem'
              }}>
                {[
                  { icon: '📱', label: 'Device Analytics' },
                  { icon: '🌍', label: 'Location Intelligence' },
                  { icon: '💳', label: 'Digital Footprint' },
                  { icon: '⚡', label: 'Utility Patterns' }
                ].map((source, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.75rem',
                    backgroundColor: 'var(--bg-secondary, #f8f9fa)',
                    borderRadius: '8px'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>{source.icon}</span>
                    <span>{source.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <button 
              style={{
                background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                color: 'white',
                border: 'none',
                padding: '1rem 2rem',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'transform 0.2s ease',
                width: '100%',
                opacity: loading ? 0.6 : 1
              }}
              onClick={requestConsent}
              disabled={loading}
              onMouseOver={(e) => !loading && (e.target.style.transform = 'translateY(-2px)')}
              onMouseOut={(e) => (e.target.style.transform = 'translateY(0)')}
            >
              {loading ? '🔄 Processing...' : '✅ Grant Consent & Start Collection'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div style={{
            backgroundColor: 'var(--bg-primary, #fff)',
            border: '1px solid var(--border-color, #e5e5e5)',
            borderRadius: '8px',
            padding: '1.5rem',
            marginBottom: '2rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>
                {collectionStatus === 'complete' ? '✅' : 
                 collectionStatus === 'error' ? '❌' : 
                 loading ? '🔄' : '⏸️'}
              </span>
              <span>
                {collectionStatus === 'idle' ? 'Ready to collect data' :
                 collectionStatus === 'complete' ? 'Data collection complete' :
                 collectionStatus === 'error' ? 'Collection failed' :
                 collectionStatus}
              </span>
            </div>
            
            <div style={{ display: 'flex', gap: '1rem' }}>
              {collectionStatus === 'idle' && (
                <button 
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: '500',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    color: 'white',
                    opacity: loading ? 0.6 : 1
                  }}
                  onClick={startDataCollection}
                  disabled={loading}
                >
                  🚀 Start Collection
                </button>
              )}
              <button 
                style={{
                  padding: '0.75rem 1.5rem',
                  border: '1px solid var(--border-color, #e5e5e5)',
                  borderRadius: '6px',
                  fontWeight: '500',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  backgroundColor: 'var(--bg-tertiary, #f8f9fa)',
                  color: 'var(--text-secondary, #666)',
                  opacity: loading ? 0.6 : 1
                }}
                onClick={revokeConsent}
                disabled={loading}
              >
                🔒 Revoke Consent
              </button>
            </div>
          </div>

          {collectedData && (
            <div style={{ marginBottom: '3rem' }}>
              <h3 style={{
                color: 'var(--text-primary, #1a1a1a)',
                marginBottom: '2rem',
                textAlign: 'center'
              }}>
                📊 Collected Data Summary
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '1.5rem'
              }}>
                {Object.entries(collectedData).map(([category, data]) => (
                  <div key={category} style={{
                    backgroundColor: 'var(--bg-primary, #fff)',
                    border: '1px solid var(--border-color, #e5e5e5)',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    transition: 'transform 0.2s ease'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      marginBottom: '1rem',
                      paddingBottom: '0.75rem',
                      borderBottom: '1px solid var(--border-color, #e5e5e5)'
                    }}>
                      <span style={{ fontSize: '1.5rem' }}>
                        {category === 'device' ? '📱' :
                         category === 'digitalFootprint' ? '💳' :
                         category === 'location' ? '🌍' : '⚡'}
                      </span>
                      <h4 style={{ color: 'var(--text-primary, #1a1a1a)', margin: 0 }}>
                        {category.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </h4>
                    </div>
                    <div>
                      {Object.entries(data).map(([key, value]) => (
                        <div key={key} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '0.5rem 0',
                          borderBottom: '1px solid rgba(0,0,0,0.05)'
                        }}>
                          <span style={{
                            color: 'var(--text-secondary, #666)',
                            fontSize: '0.9rem',
                            textTransform: 'capitalize'
                          }}>
                            {key.replace(/([A-Z])/g, ' $1').toLowerCase()}:
                          </span>
                          <span style={{
                            color: 'var(--text-primary, #1a1a1a)',
                            fontWeight: '500',
                            fontSize: '0.9rem'
                          }}>
                            {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {riskAssessment && (
            <div style={{
              background: 'linear-gradient(135deg, var(--bg-primary, #fff), var(--bg-secondary, #f8f9fa))',
              border: '2px solid #3b82f6',
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem'
              }}>
                <h3 style={{ color: 'var(--text-primary, #1a1a1a)', margin: 0 }}>
                  🎯 Risk Assessment
                </h3>
                <div style={{ textAlign: 'center' }}>
                  <div style={{
                    fontSize: '2.5rem',
                    fontWeight: '700',
                    color: '#3b82f6',
                    lineHeight: '1'
                  }}>
                    {riskAssessment.overallScore}
                  </div>
                  <div style={{
                    fontSize: '0.9rem',
                    color: 'var(--text-secondary, #666)'
                  }}>
                    Credit Score
                  </div>
                </div>
              </div>
              
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem'
              }}>
                <span style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  fontWeight: '600',
                  fontSize: '0.9rem',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981'
                }}>
                  {riskAssessment.riskLevel} Risk
                </span>
                <span style={{
                  color: 'var(--text-secondary, #666)',
                  fontSize: '0.9rem'
                }}>
                  {Math.round(riskAssessment.confidence * 100)}% Confidence
                </span>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h4 style={{
                  color: 'var(--text-primary, #1a1a1a)',
                  marginBottom: '1rem'
                }}>
                  Assessment Factors
                </h4>
                {Object.entries(riskAssessment.factors).map(([factor, score]) => (
                  <div key={factor} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    marginBottom: '0.75rem'
                  }}>
                    <span style={{
                      color: 'var(--text-secondary, #666)',
                      fontSize: '0.9rem',
                      minWidth: '140px',
                      textTransform: 'capitalize'
                    }}>
                      {factor.replace(/([A-Z])/g, ' $1').toLowerCase()}
                    </span>
                    <div style={{
                      flex: 1,
                      height: '8px',
                      backgroundColor: 'var(--bg-tertiary, #f8f9fa)',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        height: '100%',
                        background: 'linear-gradient(90deg, #3b82f6, #1d4ed8)',
                        width: `${score * 100}%`,
                        transition: 'width 0.3s ease'
                      }}></div>
                    </div>
                    <span style={{
                      color: 'var(--text-primary, #1a1a1a)',
                      fontWeight: '600',
                      fontSize: '0.9rem',
                      minWidth: '40px',
                      textAlign: 'right'
                    }}>
                      {Math.round(score * 100)}%
                    </span>
                  </div>
                ))}
              </div>

              <div>
                <h4 style={{
                  color: 'var(--text-primary, #1a1a1a)',
                  marginBottom: '1rem'
                }}>
                  Key Insights
                </h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {riskAssessment.recommendations.map((rec, index) => (
                    <li key={index} style={{
                      color: 'var(--text-secondary, #666)',
                      marginBottom: '0.5rem',
                      lineHeight: '1.5'
                    }}>
                      ✅ {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AutomaticDataCollectionDemo;
