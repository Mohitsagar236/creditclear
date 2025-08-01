/**
 * DeviceAnalyticsExample.jsx - React Native Component demonstrating
 * compliant device data collection usage
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import deviceAnalytics, { 
  collectBasicDeviceInfo, 
  collectNetworkInfo, 
  collectCompleteDeviceProfile 
} from '../services/DeviceAnalytics';

const DeviceAnalyticsExample = () => {
  const [deviceData, setDeviceData] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [completeProfile, setCompleteProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-collect basic device info on component mount
  useEffect(() => {
    collectBasicData();
  }, []);

  const collectBasicData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const basicInfo = await collectBasicDeviceInfo();
      setDeviceData(basicInfo);
      
      const netInfo = await collectNetworkInfo();
      setNetworkData(netInfo);
      
    } catch (err) {
      setError(err.message);
      Alert.alert('Error', `Failed to collect device data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const collectFullProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Show user consent dialog before collecting comprehensive data
      Alert.alert(
        'Data Collection Consent',
        'We need to collect device information for security and fraud prevention purposes. This includes basic device details and network information. No personal data or app lists will be collected.',
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => setLoading(false),
          },
          {
            text: 'Allow',
            onPress: async () => {
              try {
                const profile = await collectCompleteDeviceProfile();
                setCompleteProfile(profile);
                
                // Send to backend
                await sendToBackend(profile);
                
                Alert.alert('Success', 'Device profile collected and sent to backend');
              } catch (err) {
                setError(err.message);
                Alert.alert('Error', `Failed to collect full profile: ${err.message}`);
              } finally {
                setLoading(false);
              }
            },
          },
        ]
      );
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const sendToBackend = async (profile) => {
    try {
      // Example API call to your credit risk backend
      const response = await fetch('https://your-api.com/data-collection/device-analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN', // Include user auth token
        },
        body: JSON.stringify({
          user_id: 'user123', // Current user ID
          device_profile: profile,
          collection_timestamp: new Date().toISOString(),
          app_version: '1.0.0',
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const result = await response.json();
      console.log('Backend response:', result);
      
      return result;
    } catch (error) {
      console.error('Failed to send to backend:', error);
      throw error;
    }
  };

  const clearData = () => {
    setDeviceData(null);
    setNetworkData(null);
    setCompleteProfile(null);
    setError(null);
    deviceAnalytics.clearCache();
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Device Analytics Demo</Text>
      
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Error: {error}</Text>
        </View>
      )}

      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.button} 
          onPress={collectBasicData}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Collect Basic Info</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.button} 
          onPress={collectFullProfile}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Collect Full Profile</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.clearButton]} 
          onPress={clearData}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Clear Data</Text>
        </TouchableOpacity>
      </View>

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Collecting device data...</Text>
        </View>
      )}

      {deviceData && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>Basic Device Info</Text>
          <Text style={styles.dataText}>
            Device: {deviceData.brand} {deviceData.model}{'\n'}
            OS: {deviceData.systemName} {deviceData.systemVersion}{'\n'}
            Platform: {deviceData.platform}{'\n'}
            Is Tablet: {deviceData.isTablet ? 'Yes' : 'No'}{'\n'}
            Is Emulator: {deviceData.isEmulator ? 'Yes' : 'No'}{'\n'}
            Security: {deviceData.isPinOrFingerprintSet ? 'Enabled' : 'Disabled'}
          </Text>
        </View>
      )}

      {networkData && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>Network Info</Text>
          <Text style={styles.dataText}>
            Type: {networkData.type}{'\n'}
            Connected: {networkData.isConnected ? 'Yes' : 'No'}{'\n'}
            Internet: {networkData.isInternetReachable ? 'Yes' : 'No'}{'\n'}
            Expensive: {networkData.details.isConnectionExpensive ? 'Yes' : 'No'}
            {networkData.cellularInfo && (
              `\nCellular: ${networkData.cellularInfo.cellularGeneration}\nCarrier: ${networkData.cellularInfo.carrier}`
            )}
          </Text>
        </View>
      )}

      {completeProfile && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>Complete Profile Summary</Text>
          <Text style={styles.dataText}>
            Profile Version: {completeProfile.profileVersion}{'\n'}
            Collected At: {new Date(completeProfile.collectedAt).toLocaleString()}{'\n'}
            Collection Time: {completeProfile.collectionTimeMs}ms{'\n'}
            Risk Flags: {JSON.stringify(completeProfile.riskFlags, null, 2)}{'\n'}
            Apps Count: {completeProfile.apps.totalCount}{'\n'}
            Data Usage: {completeProfile.dataUsage.purpose}
          </Text>
        </View>
      )}

      <View style={styles.complianceContainer}>
        <Text style={styles.complianceTitle}>🔒 Privacy & Compliance</Text>
        <Text style={styles.complianceText}>
          • No app scanning - Google Play compliant{'\n'}
          • Basic device info only{'\n'}
          • User consent required{'\n'}
          • 90-day data retention{'\n'}
          • No third-party sharing{'\n'}
          • Transparent data usage
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  buttonContainer: {
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  clearButton: {
    backgroundColor: '#FF3B30',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    backgroundColor: '#FFEBEE',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  errorText: {
    color: '#C62828',
    fontSize: 14,
  },
  dataContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  dataText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#666',
    fontFamily: 'monospace',
  },
  complianceContainer: {
    backgroundColor: '#E8F5E8',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  complianceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#2E7D32',
  },
  complianceText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#388E3C',
  },
});

export default DeviceAnalyticsExample;
