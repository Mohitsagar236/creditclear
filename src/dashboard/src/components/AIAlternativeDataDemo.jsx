import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Smartphone, 
  MapPin, 
  Zap, 
  Globe, 
  MessageCircle, 
  Shield, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Cpu,
  Database,
  Activity
} from 'lucide-react';

const AIAlternativeDataDemo = () => {
  const [isCollecting, setIsCollecting] = useState(false);
  const [collectionProgress, setCollectionProgress] = useState(0);
  const [selectedUser, setSelectedUser] = useState('low_risk');
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [dataQuality, setDataQuality] = useState({});

  // Demo user profiles
  const demoUsers = {
    low_risk: {
      name: 'Sarah Chen',
      profile: 'Software Engineer, 32 years',
      avatar: '👩‍💻',
      description: 'Stable employment, premium device, consistent patterns',
      expectedRisk: 'Low'
    },
    medium_risk: {
      name: 'Raj Patel',
      profile: 'Sales Manager, 26 years',
      avatar: '👨‍💼',
      description: 'Moderate income, some irregular patterns',
      expectedRisk: 'Medium'
    },
    high_risk: {
      name: 'Alex Kumar',
      profile: 'Student, 20 years',
      avatar: '👨‍🎓',
      description: 'Limited income, outdated device, irregular patterns',
      expectedRisk: 'High'
    }
  };

  // Data collection steps
  const collectionSteps = [
    { name: 'Device Analytics', icon: Smartphone, progress: 0, status: 'pending' },
    { name: 'Location Data', icon: MapPin, progress: 0, status: 'pending' },
    { name: 'Utility Patterns', icon: Zap, progress: 0, status: 'pending' },
    { name: 'Digital Footprint', icon: Globe, progress: 0, status: 'pending' },
    { name: 'Communication', icon: MessageCircle, progress: 0, status: 'pending' },
    { name: 'AI Processing', icon: Brain, progress: 0, status: 'pending' }
  ];

  const [steps, setSteps] = useState(collectionSteps);

  // Simulate AI assessment process
  const runAIAssessment = async () => {
    setIsCollecting(true);
    setCollectionProgress(0);
    setAssessmentResult(null);
    
    // Reset steps
    setSteps(collectionSteps.map(step => ({ ...step, progress: 0, status: 'pending' })));

    // Simulate data collection for each step
    for (let i = 0; i < collectionSteps.length; i++) {
      // Update current step to collecting
      setSteps(prev => prev.map((step, index) => 
        index === i ? { ...step, status: 'collecting' } : step
      ));

      // Simulate progress for current step
      for (let progress = 0; progress <= 100; progress += 20) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setSteps(prev => prev.map((step, index) => 
          index === i ? { ...step, progress } : step
        ));
        setCollectionProgress(((i * 100) + progress) / (collectionSteps.length * 100) * 100);
      }

      // Mark step as complete
      setSteps(prev => prev.map((step, index) => 
        index === i ? { ...step, status: 'completed', progress: 100 } : step
      ));
    }

    // Generate assessment result based on selected user
    const results = {
      low_risk: {
        riskScore: 0.285,
        riskLevel: 'Low',
        confidence: 0.92,
        modelScores: {
          primary_model: 0.280,
          secondary_model: 0.290,
          device_risk: 0.150,
          behavioral_risk: 0.320
        },
        insights: [
          '✓ Premium device with latest security features',
          '✓ Consistent location patterns indicate stability',
          '✓ Regular utility payments show financial responsibility',
          '✓ Strong digital identity across multiple platforms'
        ],
        recommendations: [
          'Approve with standard terms',
          'Consider for premium product offers',
          'Standard monitoring required'
        ],
        dataQuality: {
          device_analytics: 95,
          location_data: 88,
          utility_data: 92,
          digital_footprint: 85,
          communication_data: 90
        }
      },
      medium_risk: {
        riskScore: 0.545,
        riskLevel: 'Medium',
        confidence: 0.78,
        modelScores: {
          primary_model: 0.520,
          secondary_model: 0.580,
          device_risk: 0.450,
          behavioral_risk: 0.630
        },
        insights: [
          '⚠️ Some irregular payment patterns detected',
          '✓ Device security features are enabled',
          '⚠️ Occasional travel patterns may indicate instability',
          '✓ Moderate digital footprint with verified accounts'
        ],
        recommendations: [
          'Request additional documentation',
          'Implement enhanced monitoring',
          'Consider income verification'
        ],
        dataQuality: {
          device_analytics: 78,
          location_data: 72,
          utility_data: 65,
          digital_footprint: 70,
          communication_data: 75
        }
      },
      high_risk: {
        riskScore: 0.825,
        riskLevel: 'High',
        confidence: 0.89,
        modelScores: {
          primary_model: 0.840,
          secondary_model: 0.820,
          device_risk: 0.950,
          behavioral_risk: 0.780
        },
        insights: [
          '🚨 Device emulation detected - high fraud risk',
          '🚨 Device is rooted - security compromised',
          '⚠️ Inconsistent location patterns',
          '⚠️ Limited digital footprint and verification'
        ],
        recommendations: [
          'Require comprehensive verification',
          'Implement strict monitoring',
          'Consider decline or high-risk terms',
          'Block application from emulated devices'
        ],
        dataQuality: {
          device_analytics: 45,
          location_data: 35,
          utility_data: 40,
          digital_footprint: 25,
          communication_data: 30
        }
      }
    };

    await new Promise(resolve => setTimeout(resolve, 500));
    setAssessmentResult(results[selectedUser]);
    setDataQuality(results[selectedUser].dataQuality);
    setIsCollecting(false);
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskBgColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'bg-green-100 border-green-300';
      case 'medium': return 'bg-yellow-100 border-yellow-300';
      case 'high': return 'bg-red-100 border-red-300';
      default: return 'bg-gray-100 border-gray-300';
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center space-x-3">
          <Brain className="w-10 h-10 text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900">
            AI Alternative Data Credit Risk Assessment
          </h1>
        </div>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Advanced AI model that automatically detects and analyzes alternative data from user devices, 
          combining traditional credit data with modern digital footprint analytics for comprehensive risk assessment.
        </p>
      </motion.div>

      {/* User Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Database className="w-6 h-6 mr-2 text-blue-600" />
          Select Demo User Profile
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(demoUsers).map(([key, user]) => (
            <motion.div
              key={key}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedUser(key)}
              className={`cursor-pointer rounded-lg border-2 p-4 transition-all duration-300 ${
                selectedUser === key
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center space-y-2">
                <div className="text-4xl">{user.avatar}</div>
                <h3 className="font-semibold text-lg">{user.name}</h3>
                <p className="text-sm text-gray-600">{user.profile}</p>
                <p className="text-xs text-gray-500">{user.description}</p>
                <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getRiskBgColor(user.expectedRisk)}`}>
                  Expected: {user.expectedRisk} Risk
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Assessment Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-center"
      >
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={runAIAssessment}
          disabled={isCollecting}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
        >
          <Brain className="w-6 h-6" />
          <span>
            {isCollecting ? 'Processing AI Assessment...' : 'Run AI Assessment'}
          </span>
        </motion.button>
      </motion.div>

      {/* Data Collection Progress */}
      <AnimatePresence>
        {isCollecting && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <Activity className="w-6 h-6 mr-2 text-blue-600" />
              Automatic Data Collection & AI Processing
            </h2>
            
            {/* Overall Progress */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm font-medium text-gray-700">{Math.round(collectionProgress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full"
                  style={{ width: `${collectionProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>

            {/* Individual Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {steps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`border rounded-lg p-4 ${
                      step.status === 'completed' ? 'border-green-300 bg-green-50' :
                      step.status === 'collecting' ? 'border-blue-300 bg-blue-50' :
                      'border-gray-300 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3 mb-2">
                      <Icon className={`w-5 h-5 ${
                        step.status === 'completed' ? 'text-green-600' :
                        step.status === 'collecting' ? 'text-blue-600' :
                        'text-gray-500'
                      }`} />
                      <span className="font-medium text-sm">{step.name}</span>
                      {step.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-600" />}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className={`h-2 rounded-full ${
                          step.status === 'completed' ? 'bg-green-500' :
                          step.status === 'collecting' ? 'bg-blue-500' :
                          'bg-gray-300'
                        }`}
                        style={{ width: `${step.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Assessment Results */}
      <AnimatePresence>
        {assessmentResult && !isCollecting && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Risk Score Overview */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-blue-600" />
                AI Risk Assessment Results
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-gray-900 mb-2">
                    {(assessmentResult.riskScore * 100).toFixed(1)}
                  </div>
                  <div className="text-sm text-gray-600">Risk Score (0-100)</div>
                </div>
                
                <div className="text-center">
                  <div className={`text-4xl font-bold mb-2 ${getRiskColor(assessmentResult.riskLevel)}`}>
                    {assessmentResult.riskLevel}
                  </div>
                  <div className="text-sm text-gray-600">Risk Level</div>
                </div>
                
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600 mb-2">
                    {(assessmentResult.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-sm text-gray-600">AI Confidence</div>
                </div>
              </div>
            </div>

            {/* Model Scores */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <Cpu className="w-5 h-5 mr-2 text-purple-600" />
                AI Model Component Scores
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(assessmentResult.modelScores).map(([model, score]) => (
                  <div key={model} className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium capitalize">
                        {model.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-600">
                        {(score * 100).toFixed(1)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Data Quality Scores */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-green-600" />
                Data Quality Assessment
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(dataQuality).map(([source, quality]) => (
                  <div key={source} className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium capitalize">
                        {source.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-600">{quality}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          quality >= 80 ? 'bg-green-500' :
                          quality >= 60 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${quality}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Insights and Recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-blue-600" />
                  AI Insights
                </h3>
                <div className="space-y-3">
                  {assessmentResult.insights.map((insight, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-2"
                    >
                      <div className="text-sm text-gray-700">{insight}</div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
                  Recommendations
                </h3>
                <div className="space-y-3">
                  {assessmentResult.recommendations.map((recommendation, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-2"
                    >
                      <span className="text-orange-600 mt-1">•</span>
                      <div className="text-sm text-gray-700">{recommendation}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AIAlternativeDataDemo;
