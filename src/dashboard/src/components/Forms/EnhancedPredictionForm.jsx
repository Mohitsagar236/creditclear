/**
 * Enhanced Prediction Form Component
 * 
 * Modern form with validation, real-time feedback,
 * and enhanced user experience using react-hook-form.
 */

import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  Calculator, 
  DollarSign, 
  User, 
  Calendar,
  Briefcase,
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';
import { api } from '../../services/api';
import { Input, Select } from '../ui/Input';
import Button from '../ui/Button';
import { MetricCard } from '../ui/Card';

const EnhancedPredictionForm = ({ onPredictionComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [predictionResult, setPredictionResult] = useState(null);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
    trigger,
    getValues
  } = useForm({
    mode: 'onChange',
    defaultValues: {
      AMT_INCOME_TOTAL: '',
      AMT_CREDIT: '',
      NAME_CONTRACT_TYPE: 'Cash loans',
      CODE_GENDER: 'M',
      NAME_EDUCATION_TYPE: 'Higher education',
      DAYS_BIRTH: '',
      DAYS_EMPLOYED: '',
      AMT_ANNUITY: '',
      EXT_SOURCE_1: '',
      EXT_SOURCE_2: '',
      EXT_SOURCE_3: ''
    }
  });

  // Watch form values for real-time updates
  const watchedValues = watch();

  // Prediction mutation
  const predictionMutation = useMutation({
    mutationFn: api.predict,
    onSuccess: (data) => {
      setPredictionResult(data);
      if (onPredictionComplete) {
        onPredictionComplete(data);
      }
      queryClient.invalidateQueries(['predictions']);
    },
    onError: (error) => {
      console.error('Prediction failed:', error);
    }
  });

  const onSubmit = async (data) => {
    // Convert strings to numbers where needed
    const processedData = {
      ...data,
      AMT_INCOME_TOTAL: parseFloat(data.AMT_INCOME_TOTAL),
      AMT_CREDIT: parseFloat(data.AMT_CREDIT),
      DAYS_BIRTH: parseInt(data.DAYS_BIRTH),
      DAYS_EMPLOYED: parseInt(data.DAYS_EMPLOYED),
      AMT_ANNUITY: data.AMT_ANNUITY ? parseFloat(data.AMT_ANNUITY) : null,
      EXT_SOURCE_1: data.EXT_SOURCE_1 ? parseFloat(data.EXT_SOURCE_1) : null,
      EXT_SOURCE_2: data.EXT_SOURCE_2 ? parseFloat(data.EXT_SOURCE_2) : null,
      EXT_SOURCE_3: data.EXT_SOURCE_3 ? parseFloat(data.EXT_SOURCE_3) : null,
    };

    predictionMutation.mutate(processedData);
  };

  const nextStep = async () => {
    const stepFields = getStepFields(currentStep);
    const isStepValid = await trigger(stepFields);
    
    if (isStepValid) {
      setCurrentStep(prev => Math.min(prev + 1, 3));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const getStepFields = (step) => {
    switch (step) {
      case 1:
        return ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'NAME_CONTRACT_TYPE'];
      case 2:
        return ['CODE_GENDER', 'NAME_EDUCATION_TYPE', 'DAYS_BIRTH', 'DAYS_EMPLOYED'];
      case 3:
        return ['AMT_ANNUITY', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'];
      default:
        return [];
    }
  };

  const inputVariants = {
    focus: { scale: 1.02, boxShadow: "0 0 0 3px rgba(59, 130, 246, 0.1)" },
    blur: { scale: 1, boxShadow: "0 0 0 0px rgba(59, 130, 246, 0)" }
  };

  const FormInput = ({ 
    name, 
    label, 
    type = 'text', 
    placeholder, 
    icon: Icon, 
    required = false,
    validation = {},
    hint,
    ...props 
  }) => (
    <Controller
      name={name}
      control={control}
      rules={{ required: required ? `${label} is required` : false, ...validation }}
      render={({ field, fieldState }) => (
        <Input
          {...field}
          label={label}
          type={type}
          placeholder={placeholder}
          icon={Icon}
          required={required}
          error={fieldState.error?.message}
          hint={hint}
          {...props}
        />
      )}
    />
  );

  const FormSelect = ({ name, label, options, icon: Icon, required = false, hint }) => (
    <Controller
      name={name}
      control={control}
      rules={{ required: required ? `${label} is required` : false }}
      render={({ field, fieldState }) => (
        <Select
          {...field}
          label={label}
          options={options}
          required={required}
          error={fieldState.error?.message}
          hint={hint}
        />
      )}
    />
  );

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Financial Information
            </h3>
            
            <FormInput
              name="AMT_INCOME_TOTAL"
              label="Total Income"
              type="number"
              placeholder="Enter total annual income"
              icon={DollarSign}
              required
              hint="Your total annual income from all sources"
              validation={{
                min: { value: 1, message: 'Income must be greater than 0' },
                max: { value: 10000000, message: 'Please enter a realistic income amount' }
              }}
            />

            <FormInput
              name="AMT_CREDIT"
              label="Credit Amount"
              type="number"
              placeholder="Enter requested credit amount"
              icon={Calculator}
              required
              hint="The amount of credit you are requesting"
              validation={{
                min: { value: 1, message: 'Credit amount must be greater than 0' },
                max: { value: 5000000, message: 'Please enter a realistic credit amount' }
              }}
            />

            <FormSelect
              name="NAME_CONTRACT_TYPE"
              label="Contract Type"
              hint="Choose the type of credit contract"
              required
              options={[
                { value: 'Cash loans', label: 'Cash Loan' },
                { value: 'Revolving loans', label: 'Revolving Loan' }
              ]}
            />
          </motion.div>
        );

      case 2:
        return (
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Personal Information
            </h3>

            <FormSelect
              name="CODE_GENDER"
              label="Gender"
              icon={User}
              required
              options={[
                { value: 'M', label: 'Male' },
                { value: 'F', label: 'Female' },
                { value: 'XNA', label: 'Not Specified' }
              ]}
            />

            <FormSelect
              name="NAME_EDUCATION_TYPE"
              label="Education Level"
              icon={User}
              required
              options={[
                { value: 'Secondary / secondary special', label: 'Secondary Education' },
                { value: 'Higher education', label: 'Higher Education' },
                { value: 'Incomplete higher', label: 'Incomplete Higher Education' },
                { value: 'Lower secondary', label: 'Lower Secondary' },
                { value: 'Academic degree', label: 'Academic Degree' }
              ]}
            />

            <FormInput
              name="DAYS_BIRTH"
              label="Age (in days from present, negative value)"
              type="number"
              placeholder="e.g., -10000 (approximately 27 years old)"
              icon={Calendar}
              required
              validation={{
                max: { value: -1000, message: 'Must be a negative value (days from present)' },
                min: { value: -30000, message: 'Please enter a realistic age' }
              }}
            />

            <FormInput
              name="DAYS_EMPLOYED"
              label="Employment Duration (in days, negative value)"
              type="number"
              placeholder="e.g., -2000 (approximately 5.5 years employed)"
              icon={Briefcase}
              required
              validation={{
                max: { value: 0, message: 'Must be a negative value or 0 for unemployed' },
                min: { value: -20000, message: 'Please enter a realistic employment duration' }
              }}
            />
          </motion.div>
        );

      case 3:
        return (
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Additional Information (Optional)
            </h3>

            <FormInput
              name="AMT_ANNUITY"
              label="Loan Annuity"
              type="number"
              placeholder="Annual payment amount (optional)"
              icon={DollarSign}
              validation={{
                min: { value: 0, message: 'Annuity must be positive' }
              }}
            />

            <FormInput
              name="EXT_SOURCE_1"
              label="External Source Score 1"
              type="number"
              placeholder="Score from external source 1 (0-1)"
              icon={Calculator}
              validation={{
                min: { value: 0, message: 'Score must be between 0 and 1' },
                max: { value: 1, message: 'Score must be between 0 and 1' }
              }}
            />

            <FormInput
              name="EXT_SOURCE_2"
              label="External Source Score 2"
              type="number"
              placeholder="Score from external source 2 (0-1)"
              icon={Calculator}
              validation={{
                min: { value: 0, message: 'Score must be between 0 and 1' },
                max: { value: 1, message: 'Score must be between 0 and 1' }
              }}
            />

            <FormInput
              name="EXT_SOURCE_3"
              label="External Source Score 3"
              type="number"
              placeholder="Score from external source 3 (0-1)"
              icon={Calculator}
              validation={{
                min: { value: 0, message: 'Score must be between 0 and 1' },
                max: { value: 1, message: 'Score must be between 0 and 1' }
              }}
            />
          </motion.div>
        );

      default:
        return null;
    }
  };

  if (predictionResult) {
    return (
      <motion.div 
        className="space-y-6"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="text-center bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Prediction Complete!
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Your credit risk assessment has been processed successfully.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <MetricCard
              title="Task ID"
              value={predictionResult.taskId}
              trend="neutral"
              className="text-center"
            />
            <MetricCard
              title="Status"
              value={predictionResult.status}
              trend={predictionResult.status === 'completed' ? 'up' : 'neutral'}
              className="text-center"
            />
          </div>
          
          <Button
            variant="primary"
            onClick={() => {
              setPredictionResult(null);
              setCurrentStep(1);
            }}
            className="flex items-center space-x-2 mx-auto"
          >
            <Calculator className="h-4 w-4" />
            <span>Make Another Prediction</span>
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
          <Calculator className="h-6 w-6 mr-3 text-blue-600" />
          Credit Risk Assessment
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Please fill out the form to get your credit risk prediction
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
            Step {currentStep} of 3
          </span>
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {Math.round((currentStep / 3) * 100)}% Complete
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
          <motion.div 
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full shadow-sm"
            initial={{ width: 0 }}
            animate={{ width: `${(currentStep / 3) * 100}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
        
        {/* Step indicators */}
        <div className="flex justify-between mt-4">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex flex-col items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300
                ${currentStep >= step 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                }
              `}>
                {currentStep > step ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  step
                )}
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {step === 1 ? 'Financial' : step === 2 ? 'Personal' : 'Additional'}
              </span>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        {renderStep()}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8">
          <Button
            type="button"
            variant="secondary"
            onClick={prevStep}
            disabled={currentStep === 1}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Previous</span>
          </Button>

          {currentStep < 3 ? (
            <Button
              type="button"
              variant="primary"
              onClick={nextStep}
              className="flex items-center space-x-2"
            >
              <span>Next</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              variant="success"
              disabled={!isValid || predictionMutation.isPending}
              loading={predictionMutation.isPending}
              className="flex items-center space-x-2"
            >
              {!predictionMutation.isPending && <Calculator className="h-4 w-4" />}
              <span>Submit Prediction</span>
            </Button>
          )}
        </div>
      </form>
    </motion.div>
  );
};

export default EnhancedPredictionForm;
