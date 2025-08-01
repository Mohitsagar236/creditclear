/**
 * MobileTestApp.jsx - Simple React Native Test Component
 * 
 * This is a complete, ready-to-use React Native component for testing
 * the comprehensive data collection system in a mobile app.
 * 
 * QUICK SETUP:
 * 1. Copy this file to your React Native project
 * 2. Install required dependencies (see MOBILE_TESTING_GUIDE.md)
 * 3. Import and use in your main App.js
 * 4. Run on device or simulator
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Platform,
  SafeAreaView
} from 'react-native';

// Import required React Native modules
import DeviceInfo from 'react-native-device-info';
import NetInfo from '@react-native-community/netinfo';
import { check, PERMISSIONS, RESULTS } from 'react-native-permissions';

// Import your data collection service
// Make sure ComprehensiveDataCollector.js is in your project
import {
  requestComprehensiveConsent,
  startAutomaticCollection,
  generateRiskAssessment,
  getCachedData,
  hasConsent,
  stopDataCollection
} from '../services/ComprehensiveDataCollector';

const MobileTestApp = () => {
  const [consentGranted, setConsentGranted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [collectedData, setCollectedData] = useState(null);
  const [riskScore, setRiskScore] = useState(null);

  useEffect(() => {
    // Check if consent was previously granted
    setConsentGranted(hasConsent());
    addResult('📱 Mobile test app initialized');
  }, []);

  const addResult = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestResults(prev => [...prev, { 
      id: Date.now(), 
      message, 
      timestamp 
    }]);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  // Main test function - This is what users will tap
  const runComprehensiveTest = async () => {
    try {
      setLoading(true);
      addResult('🚀 Starting comprehensive test...');

      // Step 1: Request consent
      addResult('📋 Requesting user consent...');
      const consent = await requestComprehensiveConsent();
      
      if (!consent) {
        addResult('❌ User denied consent - test stopped');
        setLoading(false);
        return;
      }

      setConsentGranted(true);
      addResult('✅ Consent granted - starting data collection');

      // Step 2: Start automatic data collection
      addResult('🔄 Starting automatic data collection...');
      const collectionResult = await startAutomaticCollection();
      
      if (collectionResult.success) {
        addResult('✅ Data collection started successfully');
      } else {
        addResult(`❌ Data collection failed: ${collectionResult.error}`);
        setLoading(false);
        return;
      }

      // Step 3: Wait for data collection to complete
      addResult('⏳ Waiting for data collection to complete...');
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Step 4: Check collected data
      const cached = getCachedData();
      setCollectedData(cached);

      if (cached && cached.lastUpdated) {
        addResult('✅ Data collection completed');
        
        // Check individual data sources
        const sources = ['digitalFootprint', 'utilityData', 'locationData', 'deviceData'];
        sources.forEach(source => {
          if (cached[source]) {
            addResult(`  ✅ ${source} collected`);
          } else {
            addResult(`  ⚠️ ${source} pending`);
          }
        });
      } else {
        addResult('⚠️ No data collected yet');
      }

      // Step 5: Generate risk assessment
      addResult('🎯 Generating risk assessment...');
      const assessment = await generateRiskAssessment();
      
      if (assessment && !assessment.error) {
        setRiskScore(assessment.overallRiskScore);
        addResult(`✅ Risk assessment: ${assessment.overallRiskScore}/100`);
        
        // Determine risk level
        let riskLevel = '🟢 Low Risk';
        if (assessment.overallRiskScore > 39) riskLevel = '🟡 Medium Risk';
        if (assessment.overallRiskScore > 69) riskLevel = '🔴 High Risk';
        
        addResult(`📊 Risk level: ${riskLevel}`);
      } else {
        addResult(`❌ Risk assessment failed: ${assessment?.error || 'Unknown error'}`);
      }

      // Step 6: Test backend connection (optional)
      addResult('🌐 Testing backend connection...');
      await testBackendConnection();

      addResult('🎉 Comprehensive test completed!');

    } catch (error) {
      addResult(`❌ Test failed: ${error.message}`);
      console.error('Test error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Test backend connection
  const testBackendConnection = async () => {
    try {
      // Replace with your actual backend URL
      const API_URL = Platform.OS === 'android' 
        ? 'http://10.0.2.2:8000'  // Android emulator
        : 'http://localhost:8000'; // iOS simulator

      const response = await fetch(`${API_URL}/comprehensive-data/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 5000
      });

      if (response.ok) {
        addResult('✅ Backend connection successful');
      } else {
        addResult(`⚠️ Backend responded with status: ${response.status}`);
      }
    } catch (error) {
      addResult(`⚠️ Backend connection failed: ${error.message}`);
      addResult('💡 Make sure your backend server is running');
    }
  };

  // Quick permission test
  const testPermissions = async () => {
    addResult('🔍 Testing device permissions...');
    
    try {
      // Test device info access
      const deviceModel = DeviceInfo.getModel();
      addResult(`📱 Device access: ✅ (${deviceModel})`);
      
      // Test network info
      const netInfo = await NetInfo.fetch();
      addResult(`🌐 Network access: ✅ (${netInfo.type})`);
      
      // Test location permission (if needed)
      if (Platform.OS === 'android') {
        const locationResult = await check(PERMISSIONS.ANDROID.ACCESS_COARSE_LOCATION);
        addResult(`📍 Location permission: ${locationResult === RESULTS.GRANTED ? '✅ Granted' : '❌ Not granted'}`);
      }
      
    } catch (error) {
      addResult(`❌ Permission test failed: ${error.message}`);
    }
  };

  // Stop data collection
  const stopCollection = async () => {
    try {
      await stopDataCollection();
      setConsentGranted(false);
      setCollectedData(null);
      setRiskScore(null);
      addResult('🛑 Data collection stopped and cache cleared');
    } catch (error) {
      addResult(`❌ Stop failed: ${error.message}`);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>📱 Credit Risk Mobile Test</Text>
          <Text style={styles.subtitle}>Test comprehensive data collection</Text>
        </View>

        {/* Status Card */}
        <View style={styles.statusCard}>
          <Text style={styles.statusText}>
            🔒 Consent: {consentGranted ? '✅ Granted' : '❌ Not granted'}
          </Text>
          {riskScore !== null && (
            <Text style={styles.statusText}>
              🎯 Risk Score: {riskScore}/100
            </Text>
          )}
        </View>

        {/* Main Test Button */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.mainButton, loading && styles.disabledButton]}
            onPress={runComprehensiveTest}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Text style={styles.mainButtonText}>
                🚀 Start Comprehensive Test
              </Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Quick Test Buttons */}
        <View style={styles.quickTestContainer}>
          <TouchableOpacity
            style={styles.quickButton}
            onPress={testPermissions}
            disabled={loading}
          >
            <Text style={styles.quickButtonText}>🔍 Test Permissions</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.quickButton, styles.stopButton]}
            onPress={stopCollection}
            disabled={loading || !consentGranted}
          >
            <Text style={styles.quickButtonText}>🛑 Stop Collection</Text>
          </TouchableOpacity>
        </View>

        {/* Data Summary */}
        {collectedData && (
          <View style={styles.dataCard}>
            <Text style={styles.cardTitle}>📊 Data Collection Status</Text>
            <Text style={styles.dataItem}>
              📱 Digital Footprint: {collectedData.digitalFootprint ? '✅' : '❌'}
            </Text>
            <Text style={styles.dataItem}>
              🔌 Utility Data: {collectedData.utilityData ? '✅' : '❌'}
            </Text>
            <Text style={styles.dataItem}>
              📍 Location Data: {collectedData.locationData ? '✅' : '❌'}
            </Text>
            <Text style={styles.dataItem}>
              ⚙️ Device Data: {collectedData.deviceData ? '✅' : '❌'}
            </Text>
          </View>
        )}

        {/* Test Results */}
        <View style={styles.resultsCard}>
          <View style={styles.resultsHeader}>
            <Text style={styles.cardTitle}>📋 Test Results</Text>
            <TouchableOpacity onPress={clearResults} style={styles.clearButton}>
              <Text style={styles.clearButtonText}>Clear</Text>
            </TouchableOpacity>
          </View>
          
          {testResults.length === 0 ? (
            <Text style={styles.noResults}>No test results yet. Run a test to see results here.</Text>
          ) : (
            testResults.slice(-10).reverse().map((result) => (
              <View key={result.id} style={styles.resultItem}>
                <Text style={styles.resultTime}>{result.timestamp}</Text>
                <Text style={styles.resultMessage}>{result.message}</Text>
              </View>
            ))
          )}
        </View>

        {/* Instructions */}
        <View style={styles.instructionsCard}>
          <Text style={styles.cardTitle}>💡 Instructions</Text>
          <Text style={styles.instruction}>
            1. Tap "Start Comprehensive Test" to begin
          </Text>
          <Text style={styles.instruction}>
            2. Grant permissions when prompted
          </Text>
          <Text style={styles.instruction}>
            3. Wait for data collection to complete
          </Text>
          <Text style={styles.instruction}>
            4. View your risk assessment results
          </Text>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: '#007bff',
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  statusCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusText: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  buttonContainer: {
    paddingHorizontal: 15,
    marginBottom: 10,
  },
  mainButton: {
    backgroundColor: '#007bff',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  mainButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  quickTestContainer: {
    flexDirection: 'row',
    paddingHorizontal: 15,
    marginBottom: 15,
    justifyContent: 'space-between',
  },
  quickButton: {
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 8,
    flex: 0.48,
    alignItems: 'center',
  },
  stopButton: {
    backgroundColor: '#dc3545',
  },
  quickButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  dataCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  dataItem: {
    fontSize: 15,
    color: '#333',
    marginBottom: 8,
    paddingLeft: 10,
  },
  resultsCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  clearButton: {
    backgroundColor: '#6c757d',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 5,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  noResults: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 20,
  },
  resultItem: {
    flexDirection: 'row',
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  resultTime: {
    fontSize: 12,
    color: '#666',
    width: 70,
    marginRight: 10,
  },
  resultMessage: {
    fontSize: 13,
    color: '#333',
    flex: 1,
  },
  instructionsCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 30,
  },
  instruction: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    paddingLeft: 10,
  },
});

export default MobileTestApp;
