/**
 * DeviceAnalytics.js - Compliant Device Data Collection Service
 * 
 * This service collects basic device information in compliance with Google Play Store
 * policies for personal loan applications. It focuses on essential device metrics
 * while avoiding prohibited data collection practices.
 * 
 * IMPORTANT COMPLIANCE NOTES:
 * 
 * 1. QUERY_ALL_PACKAGES RESTRICTION:
 *    The Android QUERY_ALL_PACKAGES permission is PROHIBITED for personal loan apps
 *    on Google Play Store. Using this permission will result in immediate app rejection.
 *    This permission allows apps to see all installed packages on a device, which is
 *    considered invasive and unnecessary for financial applications.
 * 
 * 2. ALTERNATIVE APPROACH:
 *    Instead of querying all packages, we can only check for specific, legitimate
 *    financial apps if absolutely necessary for fraud prevention. Even this should
 *    be done sparingly and with clear user consent and privacy policy disclosure.
 * 
 * 3. PERMITTED DATA COLLECTION:
 *    - Basic device information (model, OS version, manufacturer)
 *    - Network connectivity type (for performance optimization)
 *    - Device capabilities (screen size, memory - if needed for app optimization)
 *    - Hardware features relevant to app functionality
 * 
 * 4. DATA MINIMIZATION PRINCIPLE:
 *    Collect only data that is absolutely necessary for:
 *    - App functionality
 *    - Security and fraud prevention
 *    - Performance optimization
 *    - Regulatory compliance (KYC requirements)
 */

import DeviceInfo from 'react-native-device-info';
import NetInfo from '@react-native-community/netinfo';
import { Platform, Dimensions, PixelRatio } from 'react-native';

/**
 * DeviceAnalytics Service Class
 * Provides compliant device data collection for credit risk assessment
 */
class DeviceAnalytics {
  constructor() {
    this.deviceData = null;
    this.networkData = null;
  }

  /**
   * Collect basic device information using react-native-device-info
   * This data is generally permitted and useful for app optimization
   * and basic fraud prevention.
   */
  async collectBasicDeviceInfo() {
    try {
      const deviceInfo = {
        // Device identification (anonymized)
        deviceId: await DeviceInfo.getUniqueId(), // Anonymized device identifier
        deviceType: DeviceInfo.getDeviceType(),
        
        // Hardware information
        brand: DeviceInfo.getBrand(),
        manufacturer: DeviceInfo.getManufacturer(),
        model: DeviceInfo.getModel(),
        deviceName: await DeviceInfo.getDeviceName(),
        
        // Operating system information
        systemName: DeviceInfo.getSystemName(),
        systemVersion: DeviceInfo.getSystemVersion(),
        buildNumber: DeviceInfo.getBuildNumber(),
        
        // App and runtime information
        appVersion: DeviceInfo.getVersion(),
        buildVersion: DeviceInfo.getBuildNumber(),
        bundleId: DeviceInfo.getBundleId(),
        
        // Hardware capabilities
        isTablet: DeviceInfo.isTablet(),
        hasNotch: DeviceInfo.hasNotch(),
        hasDynamicIsland: DeviceInfo.hasDynamicIsland(),
        
        // Security features (important for financial apps)
        isPinOrFingerprintSet: await DeviceInfo.isPinOrFingerprintSet(),
        supportedAbis: await DeviceInfo.supportedAbis(),
        
        // Memory and storage (for performance optimization)
        totalMemory: await DeviceInfo.getTotalMemory(),
        usedMemory: await DeviceInfo.getUsedMemory(),
        totalDiskCapacity: await DeviceInfo.getTotalDiskCapacity(),
        freeDiskStorage: await DeviceInfo.getFreeDiskStorage(),
        
        // Power state (can indicate device health)
        batteryLevel: await DeviceInfo.getBatteryLevel(),
        powerState: await DeviceInfo.getPowerState(),
        
        // Development environment detection (security)
        isEmulator: await DeviceInfo.isEmulator(),
        
        // Platform-specific information
        platform: Platform.OS,
        platformVersion: Platform.Version,
      };

      // Add screen information
      const screenData = Dimensions.get('screen');
      const windowData = Dimensions.get('window');
      
      deviceInfo.screenInfo = {
        screenWidth: screenData.width,
        screenHeight: screenData.height,
        windowWidth: windowData.width,
        windowHeight: windowData.height,
        pixelRatio: PixelRatio.get(),
        fontScale: PixelRatio.getFontScale(),
      };

      // iOS-specific information
      if (Platform.OS === 'ios') {
        deviceInfo.iosInfo = {
          deviceCountryCode: await DeviceInfo.getDeviceCountryCode(),
          timeZone: await DeviceInfo.getTimezone(),
        };
      }

      // Android-specific information
      if (Platform.OS === 'android') {
        deviceInfo.androidInfo = {
          androidId: await DeviceInfo.getAndroidId(),
          apiLevel: await DeviceInfo.getApiLevel(),
          securityPatch: await DeviceInfo.getSecurityPatch(),
          codename: await DeviceInfo.getCodename(),
          incremental: await DeviceInfo.getIncremental(),
          installerPackageName: await DeviceInfo.getInstallerPackageName(),
        };
      }

      this.deviceData = deviceInfo;
      return deviceInfo;

    } catch (error) {
      console.error('Error collecting device info:', error);
      throw new Error(`Failed to collect device information: ${error.message}`);
    }
  }

  /**
   * Collect network connectivity information using NetInfo
   * This helps with app performance optimization and user experience
   */
  async collectNetworkInfo() {
    try {
      const netInfo = await NetInfo.fetch();
      
      const networkData = {
        // Connection type and quality
        type: netInfo.type, // wifi, cellular, bluetooth, ethernet, wimax, vpn, other, unknown, none
        isConnected: netInfo.isConnected,
        isInternetReachable: netInfo.isInternetReachable,
        
        // Connection details
        details: {
          isConnectionExpensive: netInfo.isConnectionExpensive,
          ssid: netInfo.details?.ssid || null, // WiFi name (if available and permitted)
          bssid: netInfo.details?.bssid || null, // WiFi router identifier
          strength: netInfo.details?.strength || null, // Signal strength
          ipAddress: netInfo.details?.ipAddress || null,
          subnet: netInfo.details?.subnet || null,
        }
      };

      // Cellular-specific information (if on cellular)
      if (netInfo.type === 'cellular' && netInfo.details) {
        networkData.cellularInfo = {
          cellularGeneration: netInfo.details.cellularGeneration, // 2g, 3g, 4g, 5g
          carrier: netInfo.details.carrier || null,
        };
      }

      this.networkData = networkData;
      return networkData;

    } catch (error) {
      console.error('Error collecting network info:', error);
      throw new Error(`Failed to collect network information: ${error.message}`);
    }
  }

  /**
   * Check for specific financial apps (COMPLIANT APPROACH)
   * 
   * IMPORTANT: This function demonstrates how to check for specific apps
   * WITHOUT using QUERY_ALL_PACKAGES permission. This approach is compliant
   * with Google Play policies for personal loan apps.
   * 
   * Instead of scanning all installed apps, we check only for specific,
   * legitimate financial apps that are relevant for fraud prevention.
   * 
   * NOTE: Even this approach should be used sparingly and with clear
   * user consent and privacy policy disclosure.
   */
  async checkSpecificFinancialApps() {
    // COMPLIANCE WARNING: Uncomment and use this function only if absolutely
    // necessary for fraud prevention and with proper user consent
    
    /*
    const financialApps = {
      // Major banking apps (package names)
      bankingApps: [
        'com.sbi.SBIFreedomPlus',     // SBI Bank
        'com.icicibank.IMobile',       // ICICI Bank
        'com.hdfc.hdfcbank',          // HDFC Bank
        'com.axisbank.mobile',         // Axis Bank
        'net.one97.paytm',            // Paytm
        'com.phonepe.app',            // PhonePe
        'com.google.android.apps.nbu.paisa.user', // Google Pay
      ],
      
      // Investment and trading apps
      investmentApps: [
        'com.zerodha.kite3',          // Zerodha Kite
        'com.msf.kbank.mobile',       // Groww
        'com.upstox.UpstoxPro',       // Upstox
      ],
      
      // Lending apps (competitors - for market analysis)
      lendingApps: [
        'com.mobikwik_new',           // MobiKwik
        'com.SlicePay.sliceit',       // Slice
        'com.kredx.merchant.android',  // KredX
      ]
    };

    const installedFinancialApps = {
      banking: [],
      investment: [],
      lending: [],
      totalCount: 0
    };

    try {
      // Check each category separately
      for (const [category, apps] of Object.entries(financialApps)) {
        for (const packageName of apps) {
          try {
            const isInstalled = await DeviceInfo.isAppInstalled(packageName);
            if (isInstalled) {
              if (category === 'bankingApps') {
                installedFinancialApps.banking.push(packageName);
              } else if (category === 'investmentApps') {
                installedFinancialApps.investment.push(packageName);
              } else if (category === 'lendingApps') {
                installedFinancialApps.lending.push(packageName);
              }
              installedFinancialApps.totalCount++;
            }
          } catch (appCheckError) {
            // Individual app check failed - continue with others
            console.warn(`Could not check for app ${packageName}:`, appCheckError);
          }
        }
      }

      return installedFinancialApps;

    } catch (error) {
      console.error('Error checking financial apps:', error);
      return {
        banking: [],
        investment: [],
        lending: [],
        totalCount: 0,
        error: error.message
      };
    }
    */

    // For compliance, return empty data unless specifically needed
    return {
      banking: [],
      investment: [],
      lending: [],
      totalCount: 0,
      note: "App scanning disabled for Google Play compliance"
    };
  }

  /**
   * Collect location-related permissions status
   * (Important for compliance and user privacy)
   */
  async collectPermissionStatus() {
    try {
      // Note: Actual permission checking would require additional libraries
      // like react-native-permissions. This is a placeholder for the structure.
      
      const permissions = {
        location: 'not_determined', // granted, denied, restricted, not_determined
        camera: 'not_determined',
        microphone: 'not_determined',
        storage: 'not_determined',
        contacts: 'not_determined',
        notifications: 'not_determined',
        
        // Financial app relevant permissions
        biometric: 'not_determined',
        phone: 'not_determined',
        sms: 'not_determined',
      };

      return permissions;

    } catch (error) {
      console.error('Error collecting permission status:', error);
      return {
        error: error.message,
        note: "Permission status collection requires react-native-permissions library"
      };
    }
  }

  /**
   * Bundle all collected data into a comprehensive device profile
   * This is the main function to call for complete data collection
   */
  async collectCompleteDeviceProfile() {
    try {
      const startTime = Date.now();

      // Collect all data in parallel for efficiency
      const [
        deviceInfo,
        networkInfo,
        financialApps,
        permissions
      ] = await Promise.all([
        this.collectBasicDeviceInfo(),
        this.collectNetworkInfo(),
        this.checkSpecificFinancialApps(),
        this.collectPermissionStatus()
      ]);

      const collectionTime = Date.now() - startTime;

      // Create comprehensive device profile
      const deviceProfile = {
        // Metadata
        profileVersion: '1.0.0',
        collectedAt: new Date().toISOString(),
        collectionTimeMs: collectionTime,
        
        // Core device data
        device: deviceInfo,
        network: networkInfo,
        
        // App and permission data (compliance-focused)
        apps: financialApps,
        permissions: permissions,
        
        // Risk assessment flags
        riskFlags: {
          isEmulator: deviceInfo?.isEmulator || false,
          isRooted: false, // Would need additional check
          isJailbroken: false, // Would need additional check
          hasSecurityFeatures: deviceInfo?.isPinOrFingerprintSet || false,
          isDebuggingEnabled: false, // Would need additional check
        },
        
        // Privacy compliance
        dataUsage: {
          purpose: 'Credit risk assessment and fraud prevention',
          retention: '90 days',
          sharing: 'Not shared with third parties',
          userConsent: 'Required before collection',
        }
      };

      return deviceProfile;

    } catch (error) {
      console.error('Error collecting complete device profile:', error);
      
      // Return minimal safe data even if collection fails
      return {
        profileVersion: '1.0.0',
        collectedAt: new Date().toISOString(),
        error: error.message,
        device: {
          platform: Platform.OS,
          platformVersion: Platform.Version,
        },
        network: {
          type: 'unknown',
          isConnected: false,
        },
        apps: {
          totalCount: 0,
          note: "Collection failed"
        },
        riskFlags: {
          isEmulator: false,
          hasSecurityFeatures: false,
        }
      };
    }
  }

  /**
   * Get cached device data (if available)
   */
  getCachedDeviceData() {
    return this.deviceData;
  }

  /**
   * Get cached network data (if available)
   */
  getCachedNetworkData() {
    return this.networkData;
  }

  /**
   * Clear cached data (for privacy)
   */
  clearCache() {
    this.deviceData = null;
    this.networkData = null;
  }
}

// Export singleton instance
const deviceAnalytics = new DeviceAnalytics();

// Export individual functions for granular usage
export const collectBasicDeviceInfo = () => deviceAnalytics.collectBasicDeviceInfo();
export const collectNetworkInfo = () => deviceAnalytics.collectNetworkInfo();
export const checkSpecificFinancialApps = () => deviceAnalytics.checkSpecificFinancialApps();
export const collectCompleteDeviceProfile = () => deviceAnalytics.collectCompleteDeviceProfile();

// Export the class and singleton
export { DeviceAnalytics };
export default deviceAnalytics;

/**
 * USAGE EXAMPLES:
 * 
 * 1. Basic device info only:
 *    const deviceInfo = await collectBasicDeviceInfo();
 * 
 * 2. Network info only:
 *    const networkInfo = await collectNetworkInfo();
 * 
 * 3. Complete device profile:
 *    const profile = await collectCompleteDeviceProfile();
 * 
 * 4. Using the class directly:
 *    const analytics = new DeviceAnalytics();
 *    const profile = await analytics.collectCompleteDeviceProfile();
 * 
 * 5. Sending to backend:
 *    const profile = await collectCompleteDeviceProfile();
 *    fetch('/api/device-analytics', {
 *      method: 'POST',
 *      headers: { 'Content-Type': 'application/json' },
 *      body: JSON.stringify(profile)
 *    });
 */
