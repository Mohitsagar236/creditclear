/**
 * LocationService.js - Compliant Coarse Location Service for Credit Applications
 * 
 * This service handles location permissions and data collection in compliance with
 * Google Play Store policies for personal loan applications.
 * 
 * IMPORTANT GOOGLE PLAY COMPLIANCE NOTES:
 * 
 * 1. FINE LOCATION IS PROHIBITED:
 *    Google Play policy for personal loan apps strictly prohibits requesting
 *    ACCESS_FINE_LOCATION permission. This would result in immediate app rejection.
 * 
 * 2. COARSE LOCATION RESTRICTIONS:
 *    ACCESS_COARSE_LOCATION is only permitted if it's essential for the app's
 *    core functionality, NOT just for credit scoring or risk assessment.
 *    Must be clearly justified and explained to users.
 * 
 * 3. PERMITTED USE CASES FOR COARSE LOCATION:
 *    - Branch/ATM locator functionality
 *    - Regional service availability checks
 *    - Fraud prevention (detecting location spoofing)
 *    - Regulatory compliance (geographic restrictions)
 * 
 * 4. USER CONSENT AND TRANSPARENCY:
 *    - Clear explanation of why location is needed
 *    - Option to deny without affecting core app functionality
 *    - Transparent privacy policy disclosure
 */

import Geolocation from 'react-native-geolocation-service';
import { 
  PERMISSIONS, 
  RESULTS, 
  request, 
  check, 
  openSettings 
} from 'react-native-permissions';
import { Platform, Alert, Linking } from 'react-native';

/**
 * LocationService Class
 * Handles coarse location requests with full compliance
 */
class LocationService {
  constructor() {
    this.hasPermission = false;
    this.lastKnownLocation = null;
    this.isRequestingLocation = false;
  }

  /**
   * Get the appropriate location permission for the platform
   */
  getLocationPermission() {
    if (Platform.OS === 'ios') {
      return PERMISSIONS.IOS.LOCATION_WHEN_IN_USE;
    } else {
      return PERMISSIONS.ANDROID.ACCESS_COARSE_LOCATION;
    }
  }

  /**
   * Check current location permission status
   */
  async checkLocationPermission() {
    try {
      const permission = this.getLocationPermission();
      const result = await check(permission);
      
      switch (result) {
        case RESULTS.UNAVAILABLE:
          console.log('Location services are not available on this device');
          return 'unavailable';
        case RESULTS.DENIED:
          console.log('Location permission has not been requested / is denied but requestable');
          return 'denied';
        case RESULTS.LIMITED:
          console.log('Location permission is limited: some functionality may not be available');
          return 'limited';
        case RESULTS.GRANTED:
          console.log('Location permission is granted');
          this.hasPermission = true;
          return 'granted';
        case RESULTS.BLOCKED:
          console.log('Location permission is denied and not requestable anymore');
          return 'blocked';
        default:
          return 'unknown';
      }
    } catch (error) {
      console.error('Error checking location permission:', error);
      return 'error';
    }
  }

  /**
   * Request location permission with proper user explanation
   * This function should only be called in response to user action
   */
  async requestLocationPermission(justification = 'branch_locator') {
    try {
      const currentStatus = await this.checkLocationPermission();
      
      if (currentStatus === 'granted') {
        return 'granted';
      }
      
      if (currentStatus === 'blocked') {
        // Permission is permanently denied, guide user to settings
        Alert.alert(
          'Location Access Required',
          'To find nearby branches and ATMs, please enable location access in your device settings.',
          [
            { text: 'Cancel', style: 'cancel' },
            { 
              text: 'Open Settings', 
              onPress: () => openSettings().catch(() => console.warn('Cannot open settings')) 
            }
          ]
        );
        return 'blocked';
      }

      // Show explanation before requesting permission
      const userConsented = await this.showLocationJustification(justification);
      if (!userConsented) {
        return 'denied';
      }

      // Request the permission
      const permission = this.getLocationPermission();
      const result = await request(permission);

      switch (result) {
        case RESULTS.GRANTED:
          this.hasPermission = true;
          console.log('Location permission granted');
          return 'granted';
        case RESULTS.DENIED:
          console.log('Location permission denied');
          return 'denied';
        case RESULTS.BLOCKED:
          console.log('Location permission blocked');
          return 'blocked';
        default:
          return 'unknown';
      }
    } catch (error) {
      console.error('Error requesting location permission:', error);
      return 'error';
    }
  }

  /**
   * Show user-friendly explanation for why location is needed
   * Returns Promise<boolean> indicating user consent
   */
  showLocationJustification(justification) {
    return new Promise((resolve) => {
      let title, message;

      switch (justification) {
        case 'branch_locator':
          title = 'Find Nearby Branches & ATMs';
          message = 'We need your approximate location to help you find the nearest bank branches and ATMs. This makes it easier to access our services when you need them.\n\nWe only use coarse location (city-level) and never track your precise movements.';
          break;
        case 'service_availability':
          title = 'Service Availability Check';
          message = 'We need to check your general area to confirm our loan services are available in your region and comply with local regulations.\n\nOnly your approximate location (city/state level) is used.';
          break;
        case 'fraud_prevention':
          title = 'Security & Fraud Prevention';
          message = 'Location information helps us detect and prevent fraudulent activities by verifying that your application is genuine.\n\nWe only collect coarse location data and never track your movements.';
          break;
        default:
          title = 'Location Access';
          message = 'We need access to your approximate location to provide better service. Your privacy is important to us - we only use coarse location data.';
      }

      Alert.alert(
        title,
        message,
        [
          { 
            text: 'Not Now', 
            style: 'cancel',
            onPress: () => resolve(false)
          },
          { 
            text: 'Allow Location', 
            onPress: () => resolve(true)
          }
        ],
        { cancelable: false }
      );
    });
  }

  /**
   * Get current coarse location
   * Returns approximate location suitable for branch finding and service availability
   */
  async getCurrentCoarseLocation(timeout = 15000) {
    return new Promise((resolve, reject) => {
      if (this.isRequestingLocation) {
        reject(new Error('Location request already in progress'));
        return;
      }

      if (!this.hasPermission) {
        reject(new Error('Location permission not granted'));
        return;
      }

      this.isRequestingLocation = true;

      const options = {
        // Use coarse accuracy settings - this provides city-level location
        accuracy: {
          android: 'coarse',  // Explicitly use coarse location
          ios: 'reduced'      // iOS equivalent of coarse accuracy
        },
        timeout: timeout,
        maximumAge: 300000,   // Accept cached location up to 5 minutes old
        enableHighAccuracy: false,  // Explicitly disable high accuracy
        distanceFilter: 1000, // Only update if moved more than 1km
      };

      Geolocation.getCurrentPosition(
        (position) => {
          this.isRequestingLocation = false;
          
          // Process the location data to ensure coarse accuracy
          const coarseLocation = this.processCoarseLocation(position);
          this.lastKnownLocation = coarseLocation;
          
          console.log('Coarse location obtained:', {
            latitude: coarseLocation.latitude.toFixed(1),
            longitude: coarseLocation.longitude.toFixed(1),
            accuracy: coarseLocation.accuracy
          });
          
          resolve(coarseLocation);
        },
        (error) => {
          this.isRequestingLocation = false;
          console.error('Error getting location:', error);
          
          // Provide user-friendly error messages
          let errorMessage = 'Unable to get your location. ';
          switch (error.code) {
            case 1: // PERMISSION_DENIED
              errorMessage += 'Location access was denied.';
              break;
            case 2: // POSITION_UNAVAILABLE
              errorMessage += 'Location services are not available.';
              break;
            case 3: // TIMEOUT
              errorMessage += 'Location request timed out. Please try again.';
              break;
            default:
              errorMessage += 'Please check your location settings and try again.';
          }
          
          reject(new Error(errorMessage));
        },
        options
      );
    });
  }

  /**
   * Process location data to ensure coarse accuracy
   * Reduces precision to city-level for compliance
   */
  processCoarseLocation(position) {
    const { latitude, longitude, accuracy, timestamp } = position.coords;
    
    // Round coordinates to ~1km precision (about 0.01 degrees)
    // This provides city-level accuracy without precise positioning
    const coarseLatitude = Math.round(latitude * 100) / 100;
    const coarseLongitude = Math.round(longitude * 100) / 100;
    
    return {
      latitude: coarseLatitude,
      longitude: coarseLongitude,
      accuracy: Math.max(accuracy || 1000, 1000), // Ensure minimum 1km accuracy
      timestamp: timestamp,
      precision: 'coarse',
      source: 'geolocation_service'
    };
  }

  /**
   * Get location for branch/ATM finder
   * This is the primary compliant use case for location in loan apps
   */
  async getLocationForBranchFinder() {
    try {
      const permissionResult = await this.requestLocationPermission('branch_locator');
      
      if (permissionResult !== 'granted') {
        throw new Error('Location permission required to find nearby branches');
      }
      
      const location = await this.getCurrentCoarseLocation();
      
      return {
        success: true,
        location: location,
        purpose: 'branch_finder',
        message: 'Location obtained for branch/ATM finder'
      };
    } catch (error) {
      console.error('Error getting location for branch finder:', error);
      return {
        success: false,
        error: error.message,
        purpose: 'branch_finder'
      };
    }
  }

  /**
   * Get location for service availability check
   * Used to verify regional service coverage
   */
  async getLocationForServiceCheck() {
    try {
      const permissionResult = await this.requestLocationPermission('service_availability');
      
      if (permissionResult !== 'granted') {
        throw new Error('Location permission required to check service availability');
      }
      
      const location = await this.getCurrentCoarseLocation();
      
      return {
        success: true,
        location: location,
        purpose: 'service_availability',
        message: 'Location obtained for service availability check'
      };
    } catch (error) {
      console.error('Error getting location for service check:', error);
      return {
        success: false,
        error: error.message,
        purpose: 'service_availability'
      };
    }
  }

  /**
   * Get location for fraud prevention (if absolutely necessary)
   * Use sparingly and with clear justification
   */
  async getLocationForFraudPrevention() {
    try {
      const permissionResult = await this.requestLocationPermission('fraud_prevention');
      
      if (permissionResult !== 'granted') {
        // Don't force location for fraud prevention - make it optional
        return {
          success: false,
          error: 'Location access declined - continuing without location verification',
          purpose: 'fraud_prevention',
          optional: true
        };
      }
      
      const location = await this.getCurrentCoarseLocation();
      
      return {
        success: true,
        location: location,
        purpose: 'fraud_prevention',
        message: 'Location obtained for security verification'
      };
    } catch (error) {
      console.error('Error getting location for fraud prevention:', error);
      return {
        success: false,
        error: error.message,
        purpose: 'fraud_prevention',
        optional: true
      };
    }
  }

  /**
   * Get last known location (cached)
   */
  getLastKnownLocation() {
    return this.lastKnownLocation;
  }

  /**
   * Clear cached location data
   */
  clearLocationData() {
    this.lastKnownLocation = null;
    this.hasPermission = false;
  }

  /**
   * Check if location services are enabled on the device
   */
  async isLocationEnabled() {
    return new Promise((resolve) => {
      Geolocation.getCurrentPosition(
        () => resolve(true),
        (error) => {
          if (error.code === 2) { // POSITION_UNAVAILABLE
            resolve(false);
          } else {
            resolve(true); // Other errors don't necessarily mean location is disabled
          }
        },
        { timeout: 1000, maximumAge: 600000 }
      );
    });
  }
}

// Export singleton instance
const locationService = new LocationService();

// Export individual functions for convenience
export const checkLocationPermission = () => locationService.checkLocationPermission();
export const requestLocationPermission = (justification) => locationService.requestLocationPermission(justification);
export const getCurrentCoarseLocation = () => locationService.getCurrentCoarseLocation();
export const getLocationForBranchFinder = () => locationService.getLocationForBranchFinder();
export const getLocationForServiceCheck = () => locationService.getLocationForServiceCheck();
export const getLocationForFraudPrevention = () => locationService.getLocationForFraudPrevention();

// Export the class and singleton
export { LocationService };
export default locationService;

/**
 * USAGE EXAMPLES:
 * 
 * 1. Branch/ATM Finder (Primary compliant use case):
 *    const result = await getLocationForBranchFinder();
 *    if (result.success) {
 *      // Show nearby branches using result.location
 *    }
 * 
 * 2. Service Availability Check:
 *    const result = await getLocationForServiceCheck();
 *    if (result.success) {
 *      // Check if services are available in this region
 *    }
 * 
 * 3. Manual Permission Request:
 *    const status = await requestLocationPermission('branch_locator');
 *    if (status === 'granted') {
 *      const location = await getCurrentCoarseLocation();
 *    }
 * 
 * 4. Check Permission Status:
 *    const status = await checkLocationPermission();
 *    console.log('Current permission status:', status);
 */
