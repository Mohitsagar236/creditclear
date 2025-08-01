"""
Data validation utilities.

This module provides comprehensive data validation utilities for the credit risk model,
including schema validation, data quality checks, and input sanitization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import re
from datetime import datetime, date
from pydantic import BaseModel, ValidationError, validator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """Result of a validation check."""
    
    def __init__(self, is_valid: bool = True, message: str = "", severity: ValidationSeverity = ValidationSeverity.INFO):
        self.is_valid = is_valid
        self.message = message
        self.severity = severity
        self.timestamp = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.message} (Valid: {self.is_valid})"
    
    def __repr__(self) -> str:
        return f"ValidationResult(is_valid={self.is_valid}, severity={self.severity}, message='{self.message}')"


class ValidationReport:
    """Collection of validation results."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.results.append(result)
    
    def add_info(self, message: str):
        """Add an info-level result."""
        self.add_result(ValidationResult(True, message, ValidationSeverity.INFO))
    
    def add_warning(self, message: str):
        """Add a warning-level result."""
        self.add_result(ValidationResult(True, message, ValidationSeverity.WARNING))
    
    def add_error(self, message: str):
        """Add an error-level result."""
        self.add_result(ValidationResult(False, message, ValidationSeverity.ERROR))
    
    def add_critical(self, message: str):
        """Add a critical-level result."""
        self.add_result(ValidationResult(False, message, ValidationSeverity.CRITICAL))
    
    @property
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return all(result.is_valid for result in self.results)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors or critical issues."""
        return any(not result.is_valid for result in self.results)
    
    @property
    def error_count(self) -> int:
        """Count of error and critical results."""
        return sum(1 for result in self.results if not result.is_valid)
    
    @property
    def warning_count(self) -> int:
        """Count of warning results."""
        return sum(1 for result in self.results if result.severity == ValidationSeverity.WARNING)
    
    def get_errors(self) -> List[ValidationResult]:
        """Get all error and critical results."""
        return [result for result in self.results if not result.is_valid]
    
    def get_warnings(self) -> List[ValidationResult]:
        """Get all warning results."""
        return [result for result in self.results if result.severity == ValidationSeverity.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'is_valid': self.is_valid,
            'total_checks': len(self.results),
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'errors': [str(result) for result in self.get_errors()],
            'warnings': [str(result) for result in self.get_warnings()],
            'all_results': [str(result) for result in self.results]
        }
    
    def __str__(self) -> str:
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        return f"Validation Report - {status} ({len(self.results)} checks, {self.error_count} errors, {self.warning_count} warnings)"


class DataValidator:
    """Comprehensive data validator for credit risk model data."""
    
    def __init__(self):
        self.report = ValidationReport()
    
    def validate_dataframe(self, df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """
        Validate a pandas DataFrame.
        
        Args:
            df: DataFrame to validate
            schema: Optional schema definition
            
        Returns:
            ValidationReport with results
        """
        self.report = ValidationReport()
        
        # Basic DataFrame checks
        if df is None:
            self.report.add_critical("DataFrame is None")
            return self.report
        
        if df.empty:
            self.report.add_error("DataFrame is empty")
            return self.report
        
        self.report.add_info(f"DataFrame has {len(df)} rows and {len(df.columns)} columns")
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            self.report.add_warning(f"Found {duplicate_count} duplicate rows")
        
        # Check for missing values
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()
        if total_missing > 0:
            self.report.add_warning(f"Found {total_missing} missing values across all columns")
            
            # Report columns with high missing value percentages
            for col in missing_counts.index:
                if missing_counts[col] > 0:
                    missing_pct = (missing_counts[col] / len(df)) * 100
                    if missing_pct > 50:
                        self.report.add_error(f"Column '{col}' has {missing_pct:.1f}% missing values")
                    elif missing_pct > 20:
                        self.report.add_warning(f"Column '{col}' has {missing_pct:.1f}% missing values")
        
        # Schema validation if provided
        if schema:
            self._validate_schema(df, schema)
        
        # Data quality checks
        self._validate_data_quality(df)
        
        return self.report
    
    def _validate_schema(self, df: pd.DataFrame, schema: Dict[str, Any]):
        """Validate DataFrame against schema."""
        # Check required columns
        required_columns = schema.get('required_columns', [])
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            self.report.add_error(f"Missing required columns: {missing_columns}")
        
        # Check column data types
        column_types = schema.get('column_types', {})
        for col, expected_type in column_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if not self._is_compatible_type(actual_type, expected_type):
                    self.report.add_warning(f"Column '{col}' has type {actual_type}, expected {expected_type}")
        
        # Check value ranges
        value_ranges = schema.get('value_ranges', {})
        for col, range_config in value_ranges.items():
            if col in df.columns:
                self._validate_value_range(df[col], col, range_config)
    
    def _validate_data_quality(self, df: pd.DataFrame):
        """Perform general data quality checks."""
        # Check for infinite values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                self.report.add_error(f"Column '{col}' contains {inf_count} infinite values")
        
        # Check for outliers using IQR method
        for col in numeric_cols:
            self._check_outliers(df[col], col)
    
    def _validate_value_range(self, series: pd.Series, col_name: str, range_config: Dict[str, Any]):
        """Validate value ranges for a series."""
        min_val = range_config.get('min')
        max_val = range_config.get('max')
        
        if min_val is not None:
            below_min = (series < min_val).sum()
            if below_min > 0:
                self.report.add_error(f"Column '{col_name}' has {below_min} values below minimum {min_val}")
        
        if max_val is not None:
            above_max = (series > max_val).sum()
            if above_max > 0:
                self.report.add_error(f"Column '{col_name}' has {above_max} values above maximum {max_val}")
    
    def _check_outliers(self, series: pd.Series, col_name: str):
        """Check for outliers using IQR method."""
        if series.dtype in ['object', 'category']:
            return
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        if outliers > 0:
            outlier_pct = (outliers / len(series)) * 100
            if outlier_pct > 10:
                self.report.add_warning(f"Column '{col_name}' has {outliers} outliers ({outlier_pct:.1f}%)")
    
    def _is_compatible_type(self, actual_type: str, expected_type: str) -> bool:
        """Check if actual data type is compatible with expected type."""
        type_mapping = {
            'int': ['int64', 'int32', 'int16', 'int8'],
            'float': ['float64', 'float32', 'float16'],
            'string': ['object', 'string'],
            'bool': ['bool'],
            'datetime': ['datetime64[ns]', 'datetime64']
        }
        
        compatible_types = type_mapping.get(expected_type, [expected_type])
        return any(compat in actual_type for compat in compatible_types)


class InputValidator:
    """Validator for API input data."""
    
    @staticmethod
    def validate_phone_number(phone: str) -> ValidationResult:
        """Validate phone number format."""
        # Remove common separators
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if it's a valid Indian mobile number
        if re.match(r'^(\+91|91)?[6-9]\d{9}$', cleaned_phone):
            return ValidationResult(True, "Valid phone number")
        else:
            return ValidationResult(False, "Invalid phone number format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return ValidationResult(True, "Valid email address")
        else:
            return ValidationResult(False, "Invalid email format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_pan_number(pan: str) -> ValidationResult:
        """Validate PAN number format."""
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if re.match(pan_pattern, pan.upper()):
            return ValidationResult(True, "Valid PAN number")
        else:
            return ValidationResult(False, "Invalid PAN number format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_user_id(user_id: str) -> ValidationResult:
        """Validate user ID format.
        
        User IDs must be alphanumeric, 4-32 characters long, and may include hyphens and underscores.
        """
        user_id_pattern = r'^[a-zA-Z0-9_-]{4,32}$'
        if re.match(user_id_pattern, user_id):
            return ValidationResult(True, "Valid user ID")
        else:
            return ValidationResult(False, "Invalid user ID format. Must be 4-32 alphanumeric characters, with optional hyphens and underscores.", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_amount(amount: Union[int, float], min_amount: float = 0) -> ValidationResult:
        """Validate monetary amount."""
        try:
            amount = float(amount)
            if amount < min_amount:
                return ValidationResult(False, f"Amount must be at least {min_amount}", ValidationSeverity.ERROR)
            if amount > 1e10:  # 10 billion
                return ValidationResult(False, "Amount seems unreasonably large", ValidationSeverity.WARNING)
            return ValidationResult(True, "Valid amount")
        except (ValueError, TypeError):
            return ValidationResult(False, "Invalid amount format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> ValidationResult:
        """Validate date range."""
        try:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            if start_date >= end_date:
                return ValidationResult(False, "Start date must be before end date", ValidationSeverity.ERROR)
            
            # Check if date range is reasonable (not more than 5 years)
            if (end_date - start_date).days > 1825:
                return ValidationResult(False, "Date range exceeds 5 years", ValidationSeverity.WARNING)
            
            return ValidationResult(True, "Valid date range")
        except (ValueError, TypeError) as e:
            return ValidationResult(False, f"Invalid date format: {e}", ValidationSeverity.ERROR)


class CreditDataValidator:
    """Specialized validator for credit-related data."""
    
    @staticmethod
    def validate_credit_score(score: Union[int, float]) -> ValidationResult:
        """Validate credit score range."""
        try:
            score = float(score)
            if 300 <= score <= 850:
                return ValidationResult(True, "Valid credit score")
            elif 0 <= score <= 1:
                # Assuming normalized score
                return ValidationResult(True, "Valid normalized credit score")
            else:
                return ValidationResult(False, "Credit score out of valid range", ValidationSeverity.ERROR)
        except (ValueError, TypeError):
            return ValidationResult(False, "Invalid credit score format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_income(income: Union[int, float], currency: str = "INR") -> ValidationResult:
        """Validate income amount."""
        try:
            income = float(income)
            
            # Minimum income thresholds by currency
            min_thresholds = {
                "INR": 10000,  # 10k INR per month
                "USD": 100,    # $100 per month
                "EUR": 100     # €100 per month
            }
            
            min_threshold = min_thresholds.get(currency, 0)
            
            if income < min_threshold:
                return ValidationResult(False, f"Income below minimum threshold for {currency}", ValidationSeverity.WARNING)
            
            # Maximum reasonable income
            max_thresholds = {
                "INR": 100000000,  # 1 crore INR per month
                "USD": 1000000,    # $1M per month
                "EUR": 1000000     # €1M per month
            }
            
            max_threshold = max_thresholds.get(currency, float('inf'))
            
            if income > max_threshold:
                return ValidationResult(False, f"Income seems unreasonably high for {currency}", ValidationSeverity.WARNING)
            
            return ValidationResult(True, "Valid income")
        except (ValueError, TypeError):
            return ValidationResult(False, "Invalid income format", ValidationSeverity.ERROR)
    
    @staticmethod
    def validate_loan_amount(loan_amount: Union[int, float], income: Union[int, float]) -> ValidationResult:
        """Validate loan amount relative to income."""
        try:
            loan_amount = float(loan_amount)
            income = float(income)
            
            if loan_amount <= 0:
                return ValidationResult(False, "Loan amount must be positive", ValidationSeverity.ERROR)
            
            # Calculate debt-to-income ratio (assuming monthly income)
            annual_income = income * 12
            dti_ratio = loan_amount / annual_income
            
            if dti_ratio > 10:  # More than 10x annual income
                return ValidationResult(False, "Loan amount is very high relative to income", ValidationSeverity.WARNING)
            elif dti_ratio > 5:  # More than 5x annual income
                return ValidationResult(True, "Loan amount is high relative to income", ValidationSeverity.WARNING)
            
            return ValidationResult(True, "Valid loan amount")
        except (ValueError, TypeError, ZeroDivisionError):
            return ValidationResult(False, "Invalid loan amount or income format", ValidationSeverity.ERROR)


def validate_prediction_input(data: Dict[str, Any]) -> ValidationReport:
    """
    Validate input data for credit risk prediction.
    
    Args:
        data: Input data dictionary
        
    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport()
    
    # Required fields
    required_fields = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'CODE_GENDER']
    for field in required_fields:
        if field not in data:
            report.add_error(f"Missing required field: {field}")
    
    # Validate specific fields
    if 'AMT_INCOME_TOTAL' in data:
        result = CreditDataValidator.validate_income(data['AMT_INCOME_TOTAL'])
        if not result.is_valid:
            report.add_result(result)
    
    if 'AMT_CREDIT' in data and 'AMT_INCOME_TOTAL' in data:
        result = CreditDataValidator.validate_loan_amount(data['AMT_CREDIT'], data['AMT_INCOME_TOTAL'])
        if not result.is_valid:
            report.add_result(result)
    
    return report


# Export functions for direct import
validate_user_id = InputValidator.validate_user_id
