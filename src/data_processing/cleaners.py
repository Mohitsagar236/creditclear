"""
Data cleaning utilities for credit risk model.

This module provides utilities for cleaning and preprocessing data, including
handling missing values and outliers.
"""

import pandas as pd
import numpy as np
from typing import List, Union


class DataCleaner:
    """A class for cleaning and preprocessing data.

    This class provides methods for handling missing values and outliers
    in both numerical and categorical data.
    """

    def __init__(self):
        """Initialize the DataCleaner."""
        self.numerical_impute_values = {}
        self.categorical_impute_values = {}

    def impute_numerical(
        self, df: pd.DataFrame, columns: List[str], strategy: str = "median"
    ) -> pd.DataFrame:
        """
        Impute missing numerical values using the specified strategy.

        Args:
            df: Input DataFrame
            columns: List of numerical columns to process
            strategy: Imputation strategy ('mean' or 'median')

        Returns:
            DataFrame with imputed values
        """
        df = df.copy()
        
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
            
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column {col} is not numeric")
            
            # Calculate impute value if not already calculated
            if col not in self.numerical_impute_values:
                if strategy == "median":
                    self.numerical_impute_values[col] = df[col].median()
                elif strategy == "mean":
                    self.numerical_impute_values[col] = df[col].mean()
                else:
                    raise ValueError("Strategy must be either 'mean' or 'median'")
            
            # Impute missing values
            df[col] = df[col].fillna(self.numerical_impute_values[col])
        
        return df

    def impute_categorical(
        self, df: pd.DataFrame, columns: List[str]
    ) -> pd.DataFrame:
        """
        Impute missing categorical values with mode.

        Args:
            df: Input DataFrame
            columns: List of categorical columns to process

        Returns:
            DataFrame with imputed values
        """
        df = df.copy()
        
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
            
            # Calculate mode if not already calculated
            if col not in self.categorical_impute_values:
                self.categorical_impute_values[col] = df[col].mode()[0]
            
            # Impute missing values
            df[col] = df[col].fillna(self.categorical_impute_values[col])
        
        return df

    def treat_outliers(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        iqr_multiplier: float = 1.5
    ) -> pd.DataFrame:
        """
        Treat outliers using the IQR method (Winsorization).

        Args:
            df: Input DataFrame
            columns: List of numerical columns to process
            iqr_multiplier: Multiplier for IQR to determine outlier bounds

        Returns:
            DataFrame with treated outliers
        """
        df = df.copy()
        
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
            
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column {col} is not numeric")
            
            # Calculate quartiles and IQR
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Calculate bounds
            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR
            
            # Cap values at bounds (Winsorization)
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df

    def get_outliers_mask(
        self, 
        df: pd.DataFrame, 
        column: str, 
        iqr_multiplier: float = 1.5
    ) -> pd.Series:
        """
        Get a boolean mask identifying outliers in a column.

        Args:
            df: Input DataFrame
            column: Column to check for outliers
            iqr_multiplier: Multiplier for IQR to determine outlier bounds

        Returns:
            Boolean Series where True indicates an outlier
        """
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column {column} is not numeric")
        
        # Calculate quartiles and IQR
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Calculate bounds
        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR
        
        # Return boolean mask of outliers
        return (df[column] < lower_bound) | (df[column] > upper_bound)
