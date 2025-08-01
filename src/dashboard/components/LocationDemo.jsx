/**
 * LocationDemo.jsx - React Native Component for Coarse Location Demo
 * 
 * This component demonstrates compliant location usage for credit applications,
 * focusing on branch/ATM finder functionality as the primary use case.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Linking,
} from 'react-native';
import locationService, { 
  checkLocationPermission,
  getLocationForBranchFinder,
  getLocationForServiceCheck,
  getLocationForFraudPrevention 
} from '../services/LocationService';

const LocationDemo = () => {
  const [permissionStatus, setPermissionStatus] = useState('unknown');
  const [isLoading, setIsLoading] = useState(false);
  const [locationData, setLocationData] = useState(null);
  const [lastAction, setLastAction] = useState('');
  const [nearbyBranches, setNearbyBranches] = useState([]);

  // Check permission status on component mount
  useEffect(() => {
    checkInitialPermissionStatus();
  }, []);

  const checkInitialPermissionStatus = async () => {
    try {
      const status = await checkLocationPermission();
      setPermissionStatus(status);
    } catch (error) {
      console.error('Error checking permission:', error);
    }
  };

  /**
   * PRIMARY USE CASE: Branch/ATM Finder
   * This is the most compliant use of location for credit applications
   */
  const handleFindNearbyBranches = async () => {
    setIsLoading(true);
    setLastAction('Finding nearby branches...');
    
    try {
      const result = await getLocationForBranchFinder();
      
      if (result.success) {
        setLocationData(result.location);
        setPermissionStatus('granted');
        
        // Simulate finding nearby branches based on location
        const mockBranches = await findNearbyBranches(result.location);
        setNearbyBranches(mockBranches);
        
        setLastAction('Found nearby branches successfully');
        
        Alert.alert(
          'Branches Found!',
          `Found ${mockBranches.length} branches near your location. Location accuracy: ${result.location.accuracy}m`,
          [{ text: 'OK' }]
        );
      } else {
        setLastAction(`Failed to find branches: ${result.error}`);
        
        if (result.error.includes('permission')) {
          Alert.alert(
            'Location Access Needed',
            'To find nearby branches and ATMs, we need access to your approximate location. This helps you locate our services when you need them.',
            [{ text: 'OK' }]
          );
        }
      }
    } catch (error) {
      setLastAction(`Error: ${error.message}`);
      console.error('Error finding branches:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * SECONDARY USE CASE: Service Availability Check
   * Used to verify if loan services are available in user's region
   */
  const handleCheckServiceAvailability = async () => {
    setIsLoading(true);
    setLastAction('Checking service availability...');
    
    try {
      const result = await getLocationForServiceCheck();
      
      if (result.success) {
        setLocationData(result.location);
        setPermissionStatus('granted');
        
        // Simulate service availability check
        const serviceInfo = await checkServiceAvailability(result.location);
        
        setLastAction('Service availability checked');
        
        Alert.alert(
          'Service Availability',
          serviceInfo.message,
          [{ text: 'OK' }]
        );
      } else {
        setLastAction(`Service check failed: ${result.error}`);
        
        // If location is denied, we can still continue with the application
        Alert.alert(
          'Service Check',
          'Unable to verify service availability for your area, but you can still continue with your application.',
          [{ text: 'Continue' }]
        );
      }
    } catch (error) {
      setLastAction(`Error: ${error.message}`);
      console.error('Error checking service availability:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * OPTIONAL USE CASE: Fraud Prevention
   * Should be optional and not block app functionality
   */
  const handleSecurityVerification = async () => {
    setIsLoading(true);
    setLastAction('Performing security verification...');
    
    try {
      const result = await getLocationForFraudPrevention();
      
      if (result.success) {
        setLocationData(result.location);
        setPermissionStatus('granted');
        setLastAction('Security verification completed');
        
        Alert.alert(
          'Security Check Complete',
          'Location verified for additional security. Your application is proceeding normally.',
          [{ text: 'OK' }]
        );
      } else {
        // This is optional - don't block the user
        setLastAction('Security check skipped (optional)');
        
        Alert.alert(
          'Security Verification',
          'Location-based security check was skipped. Your application can still proceed normally.',
          [{ text: 'Continue' }]
        );
      }
    } catch (error) {
      setLastAction(`Security check error: ${error.message}`);
      console.error('Error in security verification:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Mock function to simulate finding nearby branches
   */
  const findNearbyBranches = async (location) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock branch data based on location
    return [
      {
        id: 1,
        name: 'Main Branch',
        address: '123 Main Street',
        distance: '0.5 km',
        services: ['Loans', 'ATM', 'Customer Service']
      },
      {
        id: 2,
        name: 'Downtown Branch',
        address: '456 Business District',
        distance: '1.2 km',
        services: ['Loans', 'ATM', 'Business Banking']
      },
      {
        id: 3,
        name: 'Shopping Mall ATM',
        address: 'Central Shopping Mall',
        distance: '2.1 km',
        services: ['ATM Only']
      }
    ];
  };

  /**
   * Mock function to check service availability
   */
  const checkServiceAvailability = async (location) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Mock service availability based on location
    const lat = location.latitude;
    
    if (lat > 20 && lat < 40) { // Rough coordinates for certain regions
      return {
        available: true,
        message: 'Great! Our loan services are available in your area. You can proceed with your application.',
        region: 'Supported Region'
      };
    } else {
      return {
        available: false,
        message: 'Our services may have limited availability in your area. Please contact customer support for assistance.',
        region: 'Limited Support Region'
      };
    }
  };

  /**
   * Clear all location data
   */
  const handleClearData = () => {
    setLocationData(null);
    setNearbyBranches([]);
    setLastAction('Data cleared');
    locationService.clearLocationData();
  };

  /**
   * Open device settings for location permissions
   */
  const openLocationSettings = () => {
    Alert.alert(
      'Location Settings',
      'To enable location features, please go to your device settings and allow location access for this app.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Open Settings', 
          onPress: () => {
            Linking.openSettings().catch(() => {
              console.warn('Unable to open settings');
            });
          }
        }
      ]
    );
  };

  const getPermissionStatusColor = () => {
    switch (permissionStatus) {
      case 'granted': return '#4CAF50';
      case 'denied': return '#FF9800';
      case 'blocked': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getPermissionStatusText = () => {
    switch (permissionStatus) {
      case 'granted': return 'Location Access Granted';
      case 'denied': return 'Location Access Denied';
      case 'blocked': return 'Location Access Blocked';
      case 'unavailable': return 'Location Services Unavailable';
      default: return 'Location Permission Unknown';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>📍 Location Services Demo</Text>
      
      {/* Permission Status */}
      <View style={styles.statusContainer}>
        <View 
          style={[
            styles.statusIndicator, 
            { backgroundColor: getPermissionStatusColor() }
          ]} 
        />
        <Text style={styles.statusText}>{getPermissionStatusText()}</Text>
      </View>

      {/* Compliance Information */}
      <View style={styles.complianceContainer}>
        <Text style={styles.complianceTitle}>🔒 Google Play Compliance</Text>
        <Text style={styles.complianceText}>
          • Using ACCESS_COARSE_LOCATION only{'\n'}
          • Fine location is prohibited for loan apps{'\n'}
          • Location used for branch finder & services{'\n'}
          • User consent required for all requests{'\n'}
          • Optional for credit scoring
        </Text>
      </View>

      {/* Main Action Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={[styles.button, styles.primaryButton]} 
          onPress={handleFindNearbyBranches}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            🏦 Find Nearby Branches & ATMs
          </Text>
          <Text style={styles.buttonSubtext}>
            Primary compliant use case
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]} 
          onPress={handleCheckServiceAvailability}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            🌍 Check Service Availability
          </Text>
          <Text style={styles.buttonSubtext}>
            Verify regional coverage
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.optionalButton]} 
          onPress={handleSecurityVerification}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            🛡️ Optional Security Check
          </Text>
          <Text style={styles.buttonSubtext}>
            Fraud prevention (optional)
          </Text>
        </TouchableOpacity>
      </View>

      {/* Utility Buttons */}
      <View style={styles.utilityContainer}>
        <TouchableOpacity 
          style={[styles.utilityButton, styles.settingsButton]} 
          onPress={openLocationSettings}
        >
          <Text style={styles.utilityButtonText}>⚙️ Location Settings</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.utilityButton, styles.clearButton]} 
          onPress={handleClearData}
        >
          <Text style={styles.utilityButtonText}>🗑️ Clear Data</Text>
        </TouchableOpacity>
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>{lastAction}</Text>
        </View>
      )}

      {/* Last Action Status */}
      {!isLoading && lastAction && (
        <View style={styles.statusUpdate}>
          <Text style={styles.statusUpdateText}>Last Action: {lastAction}</Text>
        </View>
      )}

      {/* Location Data Display */}
      {locationData && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>📍 Location Data (Coarse)</Text>
          <Text style={styles.dataText}>
            Latitude: {locationData.latitude.toFixed(1)}°{'\n'}
            Longitude: {locationData.longitude.toFixed(1)}°{'\n'}
            Accuracy: {locationData.accuracy}m{'\n'}
            Precision: {locationData.precision}{'\n'}
            Timestamp: {new Date(locationData.timestamp).toLocaleTimeString()}
          </Text>
        </View>
      )}

      {/* Nearby Branches Display */}
      {nearbyBranches.length > 0 && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>🏦 Nearby Branches & ATMs</Text>
          {nearbyBranches.map((branch) => (
            <View key={branch.id} style={styles.branchItem}>
              <Text style={styles.branchName}>{branch.name}</Text>
              <Text style={styles.branchAddress}>{branch.address}</Text>
              <Text style={styles.branchDistance}>Distance: {branch.distance}</Text>
              <Text style={styles.branchServices}>
                Services: {branch.services.join(', ')}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* Usage Guidelines */}
      <View style={styles.guidelinesContainer}>
        <Text style={styles.guidelinesTitle}>💡 Usage Guidelines</Text>
        <Text style={styles.guidelinesText}>
          1. <Text style={styles.bold}>Branch Finder</Text>: Primary use case - helps users find nearby services{'\n'}
          2. <Text style={styles.bold}>Service Check</Text>: Verify regional availability and compliance{'\n'}
          3. <Text style={styles.bold}>Security</Text>: Optional fraud prevention - don't force users{'\n'}
          4. <Text style={styles.bold}>Privacy</Text>: Always explain why location is needed{'\n'}
          5. <Text style={styles.bold}>Compliance</Text>: Never use fine location for loan apps
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
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 10,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  complianceContainer: {
    backgroundColor: '#E8F5E8',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  complianceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#2E7D32',
  },
  complianceText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#388E3C',
  },
  buttonContainer: {
    marginBottom: 15,
  },
  button: {
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: '#34C759',
  },
  optionalButton: {
    backgroundColor: '#FF9500',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  buttonSubtext: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 12,
  },
  utilityContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  utilityButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  settingsButton: {
    backgroundColor: '#6C757D',
  },
  clearButton: {
    backgroundColor: '#DC3545',
  },
  utilityButtonText: {
    color: 'white',
    fontSize: 14,
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
  statusUpdate: {
    backgroundColor: '#FFF3CD',
    padding: 10,
    borderRadius: 8,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#FFC107',
  },
  statusUpdateText: {
    color: '#856404',
    fontSize: 14,
  },
  dataContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
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
  branchItem: {
    backgroundColor: '#F8F9FA',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  branchName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  branchAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  branchDistance: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
    marginBottom: 2,
  },
  branchServices: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  guidelinesContainer: {
    backgroundColor: '#E3F2FD',
    padding: 15,
    borderRadius: 8,
    marginTop: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  guidelinesTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1565C0',
  },
  guidelinesText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#1976D2',
  },
  bold: {
    fontWeight: 'bold',
  },
});

export default LocationDemo;
