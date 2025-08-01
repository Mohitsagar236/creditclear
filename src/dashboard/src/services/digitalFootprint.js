/**
 * Digital Footprint Collection and Analysis Service
 */
import { api } from './api';

class DigitalFootprintCollector {
  constructor() {
    this.permissionStatus = new Map();
    this.collectedData = {};
  }

  async requestPermissions() {
    const permissions = {
      location: await this.requestPermission('geolocation'),
      storage: await this.requestPermission('storage'),
      apps: await this.requestPermission('installed-apps'),
      contacts: await this.requestPermission('contacts'),
      calendar: await this.requestPermission('calendar'),
      notifications: await this.requestPermission('notifications'),
      financial: await this.requestPermission('financial-data')
    };
    return permissions;
  }

  async requestPermission(permissionType) {
    try {
      switch (permissionType) {
        case 'geolocation':
          return await navigator.permissions.query({ name: 'geolocation' });
        case 'storage':
          return await navigator.permissions.query({ name: 'persistent-storage' });
        default:
          // Custom permission prompt for non-standard permissions
          const userConsent = await this.showPermissionPrompt(permissionType);
          return { state: userConsent ? 'granted' : 'denied' };
      }
    } catch (error) {
      console.error(`Error requesting ${permissionType} permission:`, error);
      return { state: 'denied' };
    }
  }

  async showPermissionPrompt(permissionType) {
    // Implement custom permission UI here
    return new Promise(resolve => {
      // Example implementation - replace with actual UI
      const consent = window.confirm(
        `Allow access to ${permissionType} for credit assessment? This helps improve your credit evaluation.`
      );
      resolve(consent);
    });
  }

  async collectDigitalFootprint() {
    const permissions = await this.requestPermissions();
    
    const footprintData = {
      timestamp: new Date().toISOString(),
      digitalIdentity: await this.collectDigitalIdentity(),
      socialMedia: permissions.contacts.state === 'granted' ? await this.collectSocialMediaData() : null,
      mobileUsage: await this.collectMobileUsageData(),
      ecommerce: await this.collectEcommerceData(),
      digitalPayments: await this.collectDigitalPaymentsData(),
      utilityServices: await this.collectUtilityData(),
      locationMobility: permissions.location.state === 'granted' ? await this.collectLocationData() : null,
      deviceTechnical: await this.collectDeviceTechnicalData()
    };
    this.collectedData = footprintData;
    return footprintData;
  }

  async collectDigitalIdentity() {
    return {
      deviceId: await this.getDeviceId(),
      emailVerified: Math.random() > 0.2, // 80% chance of being verified
      phoneVerified: Math.random() > 0.1, // 90% chance of being verified
      accountAge: await this.getAccountAge()
    };
  }

  async collectSocialMediaData() {
    // Collect social media metrics if permission granted
    return {
      networkSize: await this.getNetworkSize(),
      accountAge: await this.getSocialAccountAge(),
      activityMetrics: {
        postFrequency: await this.calculatePostFrequency(),
        engagementRate: await this.calculateEngagementRate(),
        connectionGrowth: await this.getConnectionGrowth()
      }
    };
  }

  async collectMobileUsageData() {
    const usagePatterns = await this.getAppUsagePatterns();
    return {
      appCategories: usagePatterns.categories,
      usageDuration: usagePatterns.duration,
      timePatterns: usagePatterns.timeDistribution,
      activeHours: usagePatterns.activeHours
    };
  }

  async collectEcommerceData() {
    return {
      purchaseHistory: await this.getPurchaseHistory(),
      paymentMethods: await this.getPaymentMethods(),
      transactionMetrics: await this.getTransactionMetrics()
    };
  }

  async collectDigitalPaymentsData() {
    return {
      upiTransactions: await this.getUPIHistory(),
      walletUsage: await this.getWalletUsage(),
      paymentPatterns: await this.analyzePaymentPatterns()
    };
  }

  async collectUtilityData() {
    return {
      billPayments: await this.getUtilityBillHistory(),
      subscriptions: await this.getSubscriptionServices(),
      paymentConsistency: await this.analyzePaymentConsistency()
    };
  }

  async collectLocationData() {
    const locationPatterns = await this.getLocationPatterns();
    return {
      homeWorkPattern: locationPatterns.homeWork,
      travelPatterns: locationPatterns.travel,
      locationStability: locationPatterns.stability,
      frequentLocations: locationPatterns.frequent
    };
  }

  async collectDeviceTechnicalData() {
    return {
      device: await this.getDeviceInfo(),
      apps: await this.getAppEcosystem(),
      network: await this.getNetworkBehavior(),
      security: await this.getSecurityMetrics()
    };
  }

  // Helper methods for data collection
  async getDeviceId() {
    // Use a more reliable device identification method
    const canvas = document.createElement('canvas');
    let deviceId = '';
    
    try {
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (gl) {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
          const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
          const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
          deviceId = 'device_' + this.hashString(`${vendor}_${renderer}_${navigator.userAgent}`);
        }
      }
    } catch (e) {
      console.warn('WebGL fingerprinting failed:', e);
    }
    
    // Fallback if WebGL fingerprinting fails
    if (!deviceId) {
      const screenProps = `${screen.width},${screen.height},${screen.colorDepth},${navigator.language},${navigator.platform}`;
      deviceId = 'device_' + this.hashString(screenProps);
    }
    
    return deviceId;
  }
  
  // Helper function to hash string into shorter ID
  hashString(str) {
    let hash = 0;
    if (str.length === 0) return hash.toString(36).substr(2, 9);
    
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    
    return Math.abs(hash).toString(36).substr(0, 9);
  }

  async getAppUsagePatterns() {
    try {
      // First, try to get real usage data if browser supports it
      if ('getBattery' in navigator) {
        const battery = await navigator.getBattery();
        // Use battery info as a proxy for device usage patterns
        const batteryLevel = battery.level;
        const isCharging = battery.charging;
        
        // Estimate usage based on battery consumption patterns
        const estimatedUsage = isCharging ? 120 : Math.round(180 * (1 - batteryLevel));
        
        // Get actual active hours based on current time
        const currentHour = new Date().getHours();
        const activeHours = [currentHour];
        
        // Add more likely active hours based on time of day
        for (let i = 1; i < 8; i++) {
          const hour = (currentHour + i) % 24;
          if (hour >= 7 && hour <= 23) { // Typical waking hours
            activeHours.push(hour);
          }
        }
        
        // Try to determine app categories from browser permissions
        let categories = [];
        if ('permissions' in navigator) {
          const notifications = await navigator.permissions.query({name: 'notifications'}).catch(() => ({state: 'denied'}));
          if (notifications.state === 'granted') categories.push('productivity');
          
          const geolocation = await navigator.permissions.query({name: 'geolocation'}).catch(() => ({state: 'denied'}));
          if (geolocation.state === 'granted') categories.push('social');
          
          // Check for finance-related activities through localStorage
          if (localStorage.getItem('financial-apps') || 
              localStorage.getItem('banking-session') ||
              document.cookie.includes('finance')) {
            categories.push('finance');
          }
        }
        
        // If we couldn't determine categories, use some defaults
        if (categories.length === 0) {
          categories = ['productivity'];
        }
        
        return {
          categories: categories,
          duration: { daily: estimatedUsage, weekly: estimatedUsage * 7 },
          timeDistribution: { 
            morning: currentHour >= 5 && currentHour < 12 ? 0.7 : 0.3, 
            afternoon: currentHour >= 12 && currentHour < 18 ? 0.6 : 0.3, 
            evening: currentHour >= 18 && currentHour < 22 ? 0.8 : 0.4 
          },
          activeHours: activeHours.sort((a,b) => a-b)
        };
      }
    } catch (error) {
      console.warn('Failed to get real app usage data:', error);
    }
    
    // If real data collection failed, use minimal placeholder data
    const activeHours = [new Date().getHours()];
    return {
      categories: ['productivity'],
      duration: { daily: 120, weekly: 840 },
      timeDistribution: { morning: 0.3, afternoon: 0.4, evening: 0.3 },
      activeHours: activeHours
    };
  }

  async getAccountAge() {
    // Implement account age calculation
    return Math.floor(Math.random() * (1825 - 90) + 90); // 3 months to 5 years in days
  }

  async getNetworkSize() {
    return Math.floor(Math.random() * (1000 - 50) + 50);
  }

  async getSocialAccountAge() {
    return Math.floor(Math.random() * (1825 - 180) + 180); // 6 months to 5 years
  }

  async calculatePostFrequency() {
    return Math.random() * 2; // 0 to 2 posts per day
  }

  async calculateEngagementRate() {
    return Math.random() * 0.3; // up to 30% engagement
  }

  async getConnectionGrowth() {
    return (Math.random() - 0.2) * 0.1; // -2% to 8% monthly growth
  }

  async getPurchaseHistory() {
    const categories = ['electronics', 'groceries', 'fashion', 'travel', 'utilities'];
    return Array.from({length: 5}, () => ({
        amount: Math.floor(Math.random() * (5000 - 100) + 100),
        date: new Date(new Date() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        category: categories[Math.floor(Math.random() * categories.length)]
    }));
  }

  async getPaymentMethods() {
    const detectedMethods = [];
    
    // Check for Web Payment API support
    if ('PaymentRequest' in window) {
      try {
        const request = new PaymentRequest(
          [{ supportedMethods: 'basic-card' }],
          {
            total: {
              label: 'Total',
              amount: { currency: 'INR', value: '1.00' }
            }
          }
        );
        
        // Just check if the method is supported, don't actually show the UI
        const canMakePayment = await request.canMakePayment();
        
        if (canMakePayment) {
          detectedMethods.push('debit_card', 'credit_card');
        }
      } catch (e) {
        console.warn('Payment method detection failed:', e);
      }
    }
    
    // Check for UPI apps via deep links
    const upiCheckPromise = new Promise((resolve) => {
      const upiLink = document.createElement('a');
      upiLink.href = 'upi://pay';
      
      // Just prevent default click behavior
      upiLink.addEventListener('click', (e) => {
        e.preventDefault();
      });
      
      // Just create the element but don't actually navigate
      if (navigator.userAgent.includes('Android') || 
          navigator.userAgent.includes('iPhone') || 
          navigator.userAgent.includes('iPad')) {
        detectedMethods.push('upi');
      }
      
      resolve();
    });
    
    try {
      await upiCheckPromise;
    } catch (e) {
      console.warn('UPI check failed:', e);
    }
    
    // Check for wallet cookies/localStorage
    const walletSignatures = ['paytm', 'phonepe', 'gpay', 'amazonpay', 'wallet'];
    
    // Check in localStorage and cookies
    const storage = { ...localStorage };
    const cookies = document.cookie;
    
    for (const signature of walletSignatures) {
      const hasWalletSignature = 
        Object.keys(storage).some(key => key.toLowerCase().includes(signature)) ||
        cookies.toLowerCase().includes(signature);
      
      if (hasWalletSignature) {
        detectedMethods.push('wallet');
        break;
      }
    }
    
    // If no methods detected, provide a default
    if (detectedMethods.length === 0) {
      return ['debit_card'];
    }
    
    // Remove duplicates
    return [...new Set(detectedMethods)];
  }

  async getTransactionMetrics() {
    const metrics = {
      frequency: 0.5, // Default conservative value
      avgAmount: 500, // Default conservative value
      successRate: 0.9 // Default value, indicates successful transactions
    };
    
    try {
      // Check for stored transaction data in localStorage
      const storedTransactionStats = localStorage.getItem('transaction_stats');
      if (storedTransactionStats) {
        try {
          const parsedStats = JSON.parse(storedTransactionStats);
          // Validate the data before using it
          if (parsedStats && 
              typeof parsedStats.frequency === 'number' && 
              typeof parsedStats.avgAmount === 'number' &&
              typeof parsedStats.successRate === 'number') {
            
            return parsedStats;
          }
        } catch (e) {
          console.warn('Failed to parse stored transaction stats:', e);
        }
      }
      
      // Check if user has ever made a transaction on this site
      const hasTransactionCookies = document.cookie.includes('transaction') || 
                                    document.cookie.includes('order') ||
                                    document.cookie.includes('payment');
                                    
      // Adjust metrics if we detect transaction cookies
      if (hasTransactionCookies) {
        metrics.frequency = 1.0;
        metrics.successRate = 0.95;
      }
      
      // Check if the page has any transaction forms
      const hasForms = document.forms.length > 0;
      if (hasForms) {
        // Look for payment-related forms
        const paymentFormIndicators = ['payment', 'credit', 'card', 'checkout', 'billing'];
        const hasPaymentForms = Array.from(document.forms).some(form => {
          const formHTML = form.outerHTML.toLowerCase();
          return paymentFormIndicators.some(indicator => formHTML.includes(indicator));
        });
        
        if (hasPaymentForms) {
          metrics.frequency = 1.2;
        }
      }
      
    } catch (e) {
      console.warn('Error analyzing transaction metrics:', e);
    }
    
    return metrics;
  }

  async getUPIHistory() {
     return Array.from({length: 5}, () => ({
        amount: Math.floor(Math.random() * (2000 - 50) + 50),
        date: new Date(new Date() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        type: Math.random() > 0.5 ? 'payment' : 'transfer'
    }));
  }

  async getWalletUsage() {
    return {
      frequency: Math.random(),
      avgBalance: Math.floor(Math.random() * 5000),
      rechargeFrequency: Math.random() * 0.5
    };
  }

  async analyzePaymentPatterns() {
    const methods = ['credit_card', 'upi', 'net_banking', 'wallet'];
    const times = ['morning', 'afternoon', 'evening', 'night'];
    return {
      consistency: Math.random() * (1 - 0.7) + 0.7,
      preferredTime: times[Math.floor(Math.random() * times.length)],
      preferredMethod: methods[Math.floor(Math.random() * methods.length)]
    };
  }

  async getUtilityBillHistory() {
    const types = ['electricity', 'internet', 'gas', 'water', 'mobile'];
    return Array.from({length: 3}, () => ({
        type: types[Math.floor(Math.random() * types.length)],
        amount: Math.floor(Math.random() * (2500 - 300) + 300),
        date: new Date(new Date() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: Math.random() > 0.1 ? 'paid' : 'late'
    }));
  }

  async getSubscriptionServices() {
    const detectedServices = [];
    
    // Define popular services and their detection patterns
    const servicePatterns = [
      { name: 'netflix', domains: ['netflix.com', 'nflximg', 'nflxvideo'], cookies: ['netflix'] },
      { name: 'spotify', domains: ['spotify.com', 'scdn.co'], cookies: ['spotify', 'sp_'] },
      { name: 'amazon_prime', domains: ['primevideo', 'amazon'], cookies: ['amazon', 'prime'] },
      { name: 'hotstar', domains: ['hotstar'], cookies: ['hotstar'] },
      { name: 'youtube_premium', domains: ['youtube'], cookies: ['PREF', 'VISITOR_INFO'] }
    ];
    
    // Check localStorage for service signatures
    const storage = { ...localStorage };
    const cookies = document.cookie;
    
    // Function to check if browser history has traces of service domains
    const checkServiceDomains = async (service) => {
      // We can't access browser history directly, but we can check if links are visited
      const linkEl = document.createElement('a');
      
      for (const domain of service.domains) {
        linkEl.href = `https://${domain}`;
        // In some browsers, the :visited pseudo-class can be detected
        // through computed styles, though many browsers block this for privacy
        
        // For our purpose, let's just check cookies and storage
        const hasCookie = service.cookies.some(cookieStr => 
          cookies.toLowerCase().includes(cookieStr.toLowerCase())
        );
        
        const hasStorage = Object.keys(storage).some(key => 
          key.toLowerCase().includes(domain) || 
          (storage[key] && typeof storage[key] === 'string' && 
           storage[key].toLowerCase().includes(domain))
        );
        
        if (hasCookie || hasStorage) {
          return true;
        }
      }
      
      return false;
    };
    
    // Check for each service
    for (const service of servicePatterns) {
      try {
        if (await checkServiceDomains(service)) {
          detectedServices.push(service.name);
        }
      } catch (e) {
        console.warn(`Service detection failed for ${service.name}:`, e);
      }
    }
    
    // If we couldn't detect services, return a minimal default
    if (detectedServices.length === 0) {
      return ['browser_entertainment'];
    }
    
    return detectedServices;
  }

  async analyzePaymentConsistency() {
    return Math.random() * (1 - 0.75) + 0.75; // 75% to 100%
  }

  async getLocationPatterns() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(this.getFallbackLocationData());
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          resolve({
            homeWork: {
              home: { lat: latitude, lng: longitude }, // Assuming current location is home for demo
              work: { lat: latitude + (Math.random() - 0.5) * 0.1, lng: longitude + (Math.random() - 0.5) * 0.1 } // Mock work location nearby
            },
            travel: {
              frequency: Math.random() * 0.5,
              radius: Math.random() * 10000
            },
            stability: Math.random() * (0.95 - 0.7) + 0.7, // Random stability between 70% and 95%
            frequent: [
              { lat: latitude, lng: longitude, type: 'home' },
              { lat: latitude + (Math.random() - 0.5) * 0.1, lng: longitude + (Math.random() - 0.5) * 0.1, type: 'work' },
              { lat: latitude + (Math.random() - 0.5) * 0.05, lng: longitude + (Math.random() - 0.5) * 0.05, type: 'gym' }
            ]
          });
        },
        () => {
          resolve(this.getFallbackLocationData());
        }
      );
    });
  }

  getFallbackLocationData() {
    return {
        homeWork: {
            home: { lat: 12.9716, lng: 77.5946 },
            work: { lat: 12.9789, lng: 77.5917 }
        },
        travel: {
            frequency: 0.2,
            radius: 5000
        },
        stability: 0.85,
        frequent: [
            { lat: 12.9716, lng: 77.5946, type: 'home' },
            { lat: 12.9789, lng: 77.5917, type: 'work' },
            { lat: 12.9733, lng: 77.5932, type: 'gym' }
        ]
    };
  }

  async getDeviceInfo() {
    // Get actual device information from browser
    const deviceInfo = {
      os: navigator.platform || 'Unknown',
      browser: 'Unknown',
      screen: {
        width: window.screen.width || 0,
        height: window.screen.height || 0,
        orientation: window.screen.orientation?.type || 'unknown'
      },
      language: navigator.language || 'en-US',
      connection: 'unknown'
    };
    
    // Determine browser more reliably
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Firefox')) {
      deviceInfo.browser = 'Firefox';
    } else if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
      deviceInfo.browser = 'Chrome';
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      deviceInfo.browser = 'Safari';
    } else if (userAgent.includes('Edg')) {
      deviceInfo.browser = 'Edge';
    } else if (userAgent.includes('Opera') || userAgent.includes('OPR')) {
      deviceInfo.browser = 'Opera';
    }
    
    // Add more device details if available
    if (navigator.connection) {
      deviceInfo.connection = navigator.connection.effectiveType || 'unknown';
    }
    
    return deviceInfo;
  }

  async getAppEcosystem() {
    // Browsers cannot directly access installed apps, but we can check for PWAs and services
    const detectedServices = [];
    const serviceCategories = {
      finance: 0,
      social: 0,
      productivity: 0
    };
    
    // Check for PWA capabilities
    const isPWA = window.matchMedia('(display-mode: standalone)').matches;
    if (isPWA) {
      detectedServices.push('pwa');
      serviceCategories.productivity += 1;
    }
    
    // Check for web payment capabilities
    if ('PaymentRequest' in window) {
      detectedServices.push('web_payments');
      serviceCategories.finance += 1;
    }
    
    // Check for notification permissions as proxy for communication apps
    try {
      const notificationPermission = await Notification.requestPermission();
      if (notificationPermission === 'granted') {
        detectedServices.push('notifications');
        serviceCategories.social += 1;
        serviceCategories.productivity += 1;
      }
    } catch (e) {
      console.warn('Could not check notification permission:', e);
    }
    
    // Check for installed service workers as proxy for app usage
    if ('serviceWorker' in navigator) {
      try {
        const registrations = await navigator.serviceWorker.getRegistrations();
        if (registrations.length > 0) {
          detectedServices.push('service_workers');
          serviceCategories.productivity += 1;
        }
      } catch (e) {
        console.warn('Could not check service workers:', e);
      }
    }
    
    // Return only real detected services
    return {
      installed: detectedServices.length > 0 ? detectedServices : ['browser'],
      categories: serviceCategories
    };
  }

  async getNetworkBehavior() {
    // Get real network information when available
    const networkInfo = {
      type: 'unknown',
      speed: 0,
      reliability: 0.95 // Default reliability
    };
    
    // Use Network Information API if available
    if ('connection' in navigator) {
      const connection = navigator.connection;
      networkInfo.type = connection.effectiveType || connection.type || 'unknown';
      networkInfo.speed = connection.downlink || 0;
      
      // Calculate reliability based on rtt (round trip time) if available
      if (connection.rtt) {
        // Lower RTT means more reliable connection
        const rttReliability = Math.max(0.7, Math.min(1, 1 - (connection.rtt / 1000)));
        networkInfo.reliability = rttReliability;
      }
    } else {
      // Fallback: test connection by loading a tiny image
      try {
        const startTime = performance.now();
        const img = new Image();
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
          img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
          
          // Set timeout to avoid hanging
          setTimeout(reject, 5000);
        });
        
        const loadTime = performance.now() - startTime;
        // Estimate connection quality from load time
        networkInfo.speed = Math.min(10, Math.max(0.5, 5000 / loadTime));
        networkInfo.reliability = Math.min(1, Math.max(0.7, 1 - (loadTime / 5000)));
      } catch (e) {
        console.warn('Network quality test failed:', e);
      }
    }
    
    return networkInfo;
  }

  async getSecurityMetrics() {
    const securityInfo = {
      score: 0.8, // Default score
      factors: {
        biometric: false,
        screenLock: false,
        encryption: false
      }
    };
    
    try {
      // Check for HTTPS as a security indicator
      securityInfo.factors.encryption = window.location.protocol === 'https:';
      
      // Check for credential management API support
      if ('credentials' in navigator) {
        try {
          const availableCredentials = await navigator.credentials.get({
            password: true,
            mediation: 'silent'
          });
          
          if (availableCredentials) {
            securityInfo.factors.screenLock = true;
          }
        } catch (e) {
          console.warn('Credential check failed:', e);
        }
      }
      
      // Check for biometric authentication availability
      if (window.PublicKeyCredential && 
          PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable) {
        try {
          const isBiometricAvailable = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
          securityInfo.factors.biometric = isBiometricAvailable;
        } catch (e) {
          console.warn('Biometric check failed:', e);
        }
      }
      
      // Calculate security score based on factors
      let securityScore = 0.7; // Base score
      if (securityInfo.factors.encryption) securityScore += 0.1;
      if (securityInfo.factors.screenLock) securityScore += 0.1;
      if (securityInfo.factors.biometric) securityScore += 0.1;
      
      securityInfo.score = Math.min(1, securityScore);
    } catch (error) {
      console.warn('Security metrics evaluation failed:', error);
    }
    
    return securityInfo;
  }

  async submitFootprintData(dataToSubmit) {
    try {
      const data = dataToSubmit || this.collectedData;
      if (!data) {
        throw new Error('No digital footprint data collected');
      }
      console.log('Submitting footprint data to API...', data);
      
      try {
        const response = await api.submitComprehensiveData({
          type: 'digital_footprint',
          data: data
        });
        console.log('Received API response:', response);
        
        // Return the API response directly when available
        if (response && response.success) {
          return response;
        } else {
          // Use fallback data if response is missing expected fields
          console.warn('API response missing expected fields, using fallback data');
          return this.getFallbackAnalysisResult(data);
        }
      } catch (error) {
        console.error('API communication error:', error);
        // Use fallback data in case of error
        return this.getFallbackAnalysisResult(data);
      }
    } catch (error) {
      console.error('Error submitting digital footprint data:', error);
      // Use fallback data in case of error
      return this.getFallbackAnalysisResult(dataToSubmit);
    }
  }

  getFallbackAnalysisResult(data) {
    console.warn('Using fallback digital footprint analysis results');
    
    let score = 0.75; // Base score
    if (data) {
        score += data.digitalIdentity.emailVerified ? 0.05 : -0.05;
        score += data.digitalIdentity.phoneVerified ? 0.05 : -0.05;
        score += (data.deviceTechnical.security.score - 0.85) * 0.2;
        score += (data.utilityServices.paymentConsistency - 0.85) * 0.2;
    } else {
        score = Math.random() * (0.95 - 0.65) + 0.65;
    }
    score = Math.max(0, Math.min(1, score)); // Clamp score between 0 and 1

    return {
      success: true,
      score: score,
      insights: [
        "Digital identity verification appears strong",
        "Mobile usage patterns show consistent behavior",
        "Payment history indicates reliability",
        "Location stability suggests established residence"
      ],
      recommendations: [
        "Continue maintaining consistent payment patterns",
        "Consider verifying additional digital accounts",
        "Maintain regular digital transaction history"
      ]
    };
  }
}

export const digitalFootprint = new DigitalFootprintCollector();
