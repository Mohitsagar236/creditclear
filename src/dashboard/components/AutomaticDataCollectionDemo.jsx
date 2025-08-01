import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import comprehensiveDataCollector, { 
  requestComprehensiveConsent,
  startAutomaticCollection,
  generateRiskAssessment,
  getCachedData,
  hasConsent
} from '../services/ComprehensiveDataCollector';

/**
 * AutomaticDataCollectionDemo - Demonstrates comprehensive automatic data collection
 * 
 * This component shows how all data sources are automatically detected and collected
 * when user provides consent through a single permission request.
 * 
 * FEATURES DEMONSTRATED:
 * 1. Single consent flow for all data collection
 * 2. Automatic detection of digital footprint data
 * 3. Utility and service pattern analysis
 * 4. Location and mobility data (with permission)
 * 5. Device and technical specifications
 * 6. Real-time risk assessment
 * 7. Comprehensive reporting
 */

const AutomaticDataCollectionDemo = () => {
  const [loading, setLoading] = useState(false);
  const [consentGranted, setConsentGranted] = useState(false);
  const [collectionStatus, setCollectionStatus] = useState('idle');
  const [collectedData, setCollectedData] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // Check if consent was previously granted
    const checkConsentStatus = () => {
      const consentStatus = hasConsent();
      setConsentGranted(consentStatus);
      
      if (consentStatus) {
        loadCachedData();
      }
    };

    checkConsentStatus();
  }, []);

  const loadCachedData = () => {
    const cached = getCachedData();
    if (cached && cached.lastUpdated) {
      setCollectedData(cached);
      setLastUpdate(cached.lastUpdated);
      setCollectionStatus('active');
    }
  };

  /**
   * MAIN CONSENT FLOW - Single button click enables all data collection
   */
  const handleEnableSmartAssessment = async () => {
    try {
      setLoading(true);
      setError(null);

      // Request comprehensive consent - this shows the main consent dialog
      const consentGranted = await requestComprehensiveConsent();
      
      if (consentGranted) {
        setConsentGranted(true);
        setCollectionStatus('starting');
        
        // Start automatic data collection
        const collectionResult = await startAutomaticCollection();
        
        if (collectionResult.success) {
          setCollectionStatus('collecting');
          
          // Wait a moment for initial collection
          setTimeout(async () => {
            await updateCollectedData();
            await generateRiskAssessmentData();
          }, 2000);
          
        } else {
          throw new Error(collectionResult.error || 'Failed to start collection');
        }
      } else {
        setCollectionStatus('consent_denied');
      }

    } catch (err) {
      setError(err.message);
      setCollectionStatus('error');
    } finally {
      setLoading(false);
    }
  };

  /**
   * UPDATE COLLECTED DATA - Shows real-time data collection
   */
  const updateCollectedData = async () => {
    try {
      const cached = getCachedData();
      setCollectedData(cached);
      setLastUpdate(new Date().toISOString());
      setCollectionStatus('active');
    } catch (err) {
      console.error('Error updating collected data:', err);
    }
  };

  /**
   * GENERATE RISK ASSESSMENT - Shows comprehensive risk analysis
   */
  const generateRiskAssessmentData = async () => {
    try {
      const assessment = await generateRiskAssessment();
      setRiskAssessment(assessment);
    } catch (err) {
      console.error('Error generating risk assessment:', err);
    }
  };

  /**
   * REFRESH DATA - Manual refresh of all data sources
   */
  const handleRefreshData = async () => {
    if (!consentGranted) return;
    
    try {
      setLoading(true);
      await updateCollectedData();
      await generateRiskAssessmentData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * STOP COLLECTION - Revoke consent and clear data
   */
  const handleStopCollection = async () => {
    Alert.alert(
      'Stop Data Collection',
      'This will revoke consent and delete all collected data. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Stop Collection',
          style: 'destructive',
          onPress: async () => {
            try {
              await comprehensiveDataCollector.stopDataCollection();
              setConsentGranted(false);
              setCollectionStatus('idle');
              setCollectedData(null);
              setRiskAssessment(null);
              setLastUpdate(null);
            } catch (err) {
              setError(err.message);
            }
          }
        }
      ]
    );
  };

  /**
   * RENDER DATA SUMMARY - Shows what data is being collected
   */
  const renderDataSummary = () => {
    if (!collectedData) return null;

    const summary = {
      'Digital Footprint': collectedData.digitalFootprint ? '✅ Collected' : '⏳ Collecting...',
      'Device Analytics': collectedData.deviceData ? '✅ Collected' : '⏳ Collecting...',
      'Location Patterns': collectedData.locationData ? '✅ Collected' : '⏳ Collecting...',
      'Utility Patterns': collectedData.utilityData ? '✅ Collected' : '⏳ Collecting...'
    };

    return (
      <View style={styles.summaryContainer}>
        <Text style={styles.summaryTitle}>📊 Data Collection Status</Text>
        {Object.entries(summary).map(([key, value]) => (
          <View key={key} style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>{key}:</Text>
            <Text style={styles.summaryValue}>{value}</Text>
          </View>
        ))}
        {lastUpdate && (
          <Text style={styles.lastUpdate}>
            Last updated: {new Date(lastUpdate).toLocaleTimeString()}
          </Text>
        )}
      </View>
    );
  };

  /**
   * RENDER RISK ASSESSMENT - Shows comprehensive risk analysis
   */
  const renderRiskAssessment = () => {
    if (!riskAssessment) return null;

    const getRiskColor = (score) => {
      if (score <= 39) return '#28a745'; // Green
      if (score <= 69) return '#ffc107'; // Yellow
      return '#dc3545'; // Red
    };

    const getRiskLevel = (score) => {
      if (score <= 39) return 'Low Risk';
      if (score <= 69) return 'Medium Risk';
      return 'High Risk';
    };

    return (
      <View style={styles.riskContainer}>
        <Text style={styles.riskTitle}>🛡️ Risk Assessment</Text>
        
        <View style={styles.riskScoreContainer}>
          <Text style={styles.riskScoreLabel}>Overall Risk Score</Text>
          <Text style={[
            styles.riskScore,
            { color: getRiskColor(riskAssessment.overallRiskScore) }
          ]}>
            {riskAssessment.overallRiskScore}/100
          </Text>
          <Text style={[
            styles.riskLevel,
            { color: getRiskColor(riskAssessment.overallRiskScore) }
          ]}>
            {getRiskLevel(riskAssessment.overallRiskScore)}
          </Text>
        </View>

        <View style={styles.riskBreakdown}>
          <Text style={styles.riskBreakdownTitle}>Risk Breakdown:</Text>
          <Text style={styles.riskDetail}>📱 Digital Footprint: {riskAssessment.digitalFootprintRisk}/100</Text>
          <Text style={styles.riskDetail}>🔐 Device Security: {riskAssessment.deviceSecurityRisk}/100</Text>
          <Text style={styles.riskDetail}>📍 Location Stability: {riskAssessment.locationStabilityRisk}/100</Text>
          <Text style={styles.riskDetail}>📊 Behavior Patterns: {riskAssessment.behaviorPatternRisk}/100</Text>
        </View>

        {riskAssessment.riskFactors && riskAssessment.riskFactors.length > 0 && (
          <View style={styles.riskFactors}>
            <Text style={styles.riskFactorsTitle}>⚠️ Risk Factors:</Text>
            {riskAssessment.riskFactors.map((factor, index) => (
              <Text key={index} style={styles.riskFactor}>• {factor}</Text>
            ))}
          </View>
        )}

        {riskAssessment.positiveIndicators && riskAssessment.positiveIndicators.length > 0 && (
          <View style={styles.positiveIndicators}>
            <Text style={styles.positiveTitle}>✅ Positive Indicators:</Text>
            {riskAssessment.positiveIndicators.map((indicator, index) => (
              <Text key={index} style={styles.positiveIndicator}>• {indicator}</Text>
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🤖 Smart Credit Assessment</Text>
        <Text style={styles.subtitle}>
          Automatic detection of all data sources with single consent
        </Text>
      </View>

      {/* MAIN CONSENT BUTTON */}
      {!consentGranted && (
        <View style={styles.consentSection}>
          <Text style={styles.consentTitle}>Enable Smart Assessment</Text>
          <Text style={styles.consentDescription}>
            Get instant loan approval with comprehensive but private analysis of:
          </Text>
          
          <View style={styles.featureList}>
            <Text style={styles.feature}>📱 Digital Footprint Analysis</Text>
            <Text style={styles.feature}>🌐 Location & Mobility Patterns</Text>
            <Text style={styles.feature}>💳 Payment Behavior Indicators</Text>
            <Text style={styles.feature}>🔒 Device Security Assessment</Text>
            <Text style={styles.feature}>📊 Utility Usage Patterns</Text>
            <Text style={styles.feature}>🛡️ Real-time Risk Scoring</Text>
          </View>

          <TouchableOpacity
            style={styles.enableButton}
            onPress={handleEnableSmartAssessment}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.enableButtonText}>Enable Smart Assessment</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.privacyNote}>
            🔒 Your data stays private and secure. Used only for credit assessment.
          </Text>
        </View>
      )}

      {/* COLLECTION STATUS */}
      {consentGranted && (
        <View style={styles.statusSection}>
          <Text style={styles.statusTitle}>Collection Status: {collectionStatus}</Text>
          
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={styles.refreshButton}
              onPress={handleRefreshData}
              disabled={loading}
            >
              <Text style={styles.refreshButtonText}>🔄 Refresh Data</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.stopButton}
              onPress={handleStopCollection}
            >
              <Text style={styles.stopButtonText}>⏹️ Stop Collection</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* DATA SUMMARY */}
      {renderDataSummary()}

      {/* RISK ASSESSMENT */}
      {renderRiskAssessment()}

      {/* ERROR DISPLAY */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>❌ Error</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* WHAT'S BEING COLLECTED */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>What's Being Collected Automatically?</Text>
        
        <View style={styles.infoCategory}>
          <Text style={styles.infoCategory}>📱 Digital Footprint Data</Text>
          <Text style={styles.infoDetail}>• Device usage patterns and stability</Text>
          <Text style={styles.infoDetail}>• App ecosystem analysis (compliant)</Text>
          <Text style={styles.infoDetail}>• Security features assessment</Text>
          <Text style={styles.infoDetail}>• Digital payment behavior indicators</Text>
        </View>

        <View style={styles.infoCategory}>
          <Text style={styles.infoCategoryTitle}>🌐 Location & Mobility Data</Text>
          <Text style={styles.infoDetail}>• Coarse location (city-level only)</Text>
          <Text style={styles.infoDetail}>• Movement stability patterns</Text>
          <Text style={styles.infoDetail}>• Service availability verification</Text>
          <Text style={styles.infoDetail}>• No precise tracking or history</Text>
        </View>

        <View style={styles.infoCategory}>
          <Text style={styles.infoCategoryTitle}>💳 Utility & Service Data</Text>
          <Text style={styles.infoDetail}>• Network connectivity patterns</Text>
          <Text style={styles.infoDetail}>• Service reliability indicators</Text>
          <Text style={styles.infoDetail}>• Payment method preferences</Text>
          <Text style={styles.infoDetail}>• Subscription behavior patterns</Text>
        </View>

        <View style={styles.infoCategory}>
          <Text style={styles.infoCategoryTitle}>🔧 Device & Technical Data</Text>
          <Text style={styles.infoDetail}>• Hardware specifications</Text>
          <Text style={styles.infoDetail}>• Performance metrics</Text>
          <Text style={styles.infoDetail}>• Security configuration</Text>
          <Text style={styles.infoDetail}>• Fraud prevention indicators</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  consentSection: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    elevation: 2,
  },
  consentTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  consentDescription: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
    textAlign: 'center',
  },
  featureList: {
    marginBottom: 20,
  },
  feature: {
    fontSize: 14,
    color: '#555',
    marginBottom: 5,
    paddingLeft: 10,
  },
  enableButton: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  enableButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  privacyNote: {
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  statusSection: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    elevation: 2,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  refreshButton: {
    backgroundColor: '#28a745',
    padding: 10,
    borderRadius: 5,
    flex: 0.45,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  stopButton: {
    backgroundColor: '#dc3545',
    padding: 10,
    borderRadius: 5,
    flex: 0.45,
    alignItems: 'center',
  },
  stopButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  summaryContainer: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    elevation: 2,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#555',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  lastUpdate: {
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
    marginTop: 10,
    fontStyle: 'italic',
  },
  riskContainer: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    elevation: 2,
  },
  riskTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  riskScoreContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  riskScoreLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  riskScore: {
    fontSize: 36,
    fontWeight: 'bold',
  },
  riskLevel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 5,
  },
  riskBreakdown: {
    marginBottom: 15,
  },
  riskBreakdownTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  riskDetail: {
    fontSize: 14,
    color: '#555',
    marginBottom: 3,
  },
  riskFactors: {
    marginBottom: 15,
  },
  riskFactorsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#dc3545',
    marginBottom: 8,
  },
  riskFactor: {
    fontSize: 14,
    color: '#dc3545',
    marginBottom: 3,
  },
  positiveIndicators: {
    marginBottom: 15,
  },
  positiveTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#28a745',
    marginBottom: 8,
  },
  positiveIndicator: {
    fontSize: 14,
    color: '#28a745',
    marginBottom: 3,
  },
  errorContainer: {
    backgroundColor: '#ffe6e6',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ffcccc',
  },
  errorTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#dc3545',
    marginBottom: 8,
  },
  errorText: {
    fontSize: 14,
    color: '#dc3545',
  },
  infoSection: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    elevation: 2,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoCategory: {
    marginBottom: 15,
  },
  infoCategoryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 8,
  },
  infoDetail: {
    fontSize: 13,
    color: '#666',
    marginBottom: 3,
    paddingLeft: 10,
  },
});

export default AutomaticDataCollectionDemo;
