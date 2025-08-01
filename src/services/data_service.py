"""
Enhanced data service for credit risk model.

This module provides advanced data management, caching, and processing
capabilities for the credit risk assessment system.
"""

import pandas as pd
import numpy as np
import redis
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import gzip
from concurrent.futures import ThreadPoolExecutor
import uuid

from src.utils.config import get_config
from src.data_processing.feature_engineering import FeatureEngineer
from src.data_processing.cleaners import DataCleaner
from src.utils.validators import DataValidator, ValidationReport

logger = logging.getLogger(__name__)
config = get_config()


class DataSource(Enum):
    """Enumeration of data sources."""
    USER_INPUT = "user_input"
    ACCOUNT_AGGREGATOR = "account_aggregator"
    DEVICE_ANALYTICS = "device_analytics"
    LOCATION_SERVICES = "location_services"
    DIGITAL_FOOTPRINT = "digital_footprint"
    CACHE = "cache"


@dataclass
class DataQuality:
    """Data quality metrics."""
    completeness: float  # Percentage of non-null values
    consistency: float   # Consistency score
    accuracy: float     # Accuracy score
    timeliness: float   # Data freshness score
    overall_score: float
    issues: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessedData:
    """Container for processed data with metadata."""
    data: pd.DataFrame
    feature_names: List[str]
    data_sources: List[DataSource]
    processing_time: float
    quality_score: DataQuality
    cache_key: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data.to_dict(),
            "feature_names": self.feature_names,
            "data_sources": [ds.value for ds in self.data_sources],
            "processing_time": self.processing_time,
            "quality_score": self.quality_score.to_dict(),
            "cache_key": self.cache_key,
            "timestamp": self.timestamp.isoformat()
        }


class DataCache:
    """Advanced caching system for processed data."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0,
            "evictions": 0
        }
    
    def _generate_cache_key(self, data: Dict[str, Any], processing_options: Dict[str, Any]) -> str:
        """Generate a unique cache key for data and processing options."""
        cache_input = {
            "data": data,
            "options": processing_options,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d-%H")  # Hour-based caching
        }
        
        cache_string = json.dumps(cache_input, sort_keys=True, default=str)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    async def get(self, cache_key: str) -> Optional[ProcessedData]:
        """Retrieve data from cache."""
        try:
            # Try Redis first
            if self.redis_client:
                cached_data = self.redis_client.get(f"data_cache:{cache_key}")
                if cached_data:
                    data = pickle.loads(gzip.decompress(cached_data))
                    self.cache_stats["hits"] += 1
                    logger.info(f"Cache HIT (Redis): {cache_key}")
                    return data
            
            # Try local cache
            if cache_key in self.local_cache:
                cached_item = self.local_cache[cache_key]
                if datetime.utcnow() < cached_item["expires_at"]:
                    self.cache_stats["hits"] += 1
                    logger.info(f"Cache HIT (Local): {cache_key}")
                    return cached_item["data"]
                else:
                    # Remove expired item
                    del self.local_cache[cache_key]
            
            self.cache_stats["misses"] += 1
            logger.info(f"Cache MISS: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, cache_key: str, data: ProcessedData, ttl: int = 3600):
        """Store data in cache."""
        try:
            # Store in Redis if available
            if self.redis_client:
                compressed_data = gzip.compress(pickle.dumps(data))
                self.redis_client.setex(f"data_cache:{cache_key}", ttl, compressed_data)
            
            # Store in local cache
            self.local_cache[cache_key] = {
                "data": data,
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
            }
            
            self.cache_stats["stores"] += 1
            logger.info(f"Data cached: {cache_key}")
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "local_cache_size": len(self.local_cache)
        }


class EnhancedDataService:
    """Enhanced data service with caching, validation, and processing."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.data_cleaner = DataCleaner()
        self.data_validator = DataValidator()
        
        # Initialize Redis cache if available
        try:
            redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.database,
                password=config.redis.password,
                decode_responses=False  # We're using binary data
            )
            redis_client.ping()  # Test connection
        except Exception as e:
            logger.warning(f"Redis not available, using local cache only: {e}")
            redis_client = None
        
        self.cache = DataCache(redis_client)
        self.processing_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "processing_errors": 0,
            "average_processing_time": 0
        }
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_data(
        self,
        input_data: Dict[str, Any],
        data_sources: List[DataSource] = None,
        enable_caching: bool = True,
        processing_options: Dict[str, Any] = None
    ) -> ProcessedData:
        """
        Process input data with caching and validation.
        
        Args:
            input_data: Raw input data dictionary
            data_sources: List of data sources used
            enable_caching: Whether to use caching
            processing_options: Processing configuration options
            
        Returns:
            ProcessedData object with results and metadata
        """
        start_time = datetime.utcnow()
        processing_start = datetime.utcnow().timestamp()
        
        # Set defaults
        if data_sources is None:
            data_sources = [DataSource.USER_INPUT]
        if processing_options is None:
            processing_options = {}
        
        self.processing_stats["total_requests"] += 1
        
        try:
            # Generate cache key
            cache_key = self.cache._generate_cache_key(input_data, processing_options)
            
            # Check cache first
            if enable_caching:
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    self.processing_stats["cache_hits"] += 1
                    return cached_data
            
            # Process data
            processed_data = await self._process_data_internal(
                input_data, data_sources, processing_options, cache_key
            )
            
            # Cache the result
            if enable_caching:
                await self.cache.set(cache_key, processed_data)
            
            # Update stats
            processing_time = datetime.utcnow().timestamp() - processing_start
            self._update_processing_stats(processing_time)
            
            return processed_data
            
        except Exception as e:
            self.processing_stats["processing_errors"] += 1
            logger.error(f"Data processing error: {e}", exc_info=True)
            raise
    
    async def _process_data_internal(
        self,
        input_data: Dict[str, Any],
        data_sources: List[DataSource],
        processing_options: Dict[str, Any],
        cache_key: str
    ) -> ProcessedData:
        """Internal data processing logic."""
        processing_start = datetime.utcnow().timestamp()
        
        # Convert to DataFrame
        df = pd.DataFrame([input_data])
        
        # Data validation
        validation_report = self.data_validator.validate_dataframe(df)
        
        # Data cleaning
        if processing_options.get("clean_data", True):
            df = await self._run_in_executor(self._clean_data, df)
        
        # Feature engineering
        if processing_options.get("engineer_features", True):
            df = await self._run_in_executor(self._engineer_features, df)
        
        # Calculate data quality
        quality_score = self._calculate_data_quality(df, validation_report)
        
        processing_time = datetime.utcnow().timestamp() - processing_start
        
        return ProcessedData(
            data=df,
            feature_names=list(df.columns),
            data_sources=data_sources,
            processing_time=processing_time,
            quality_score=quality_score,
            cache_key=cache_key,
            timestamp=datetime.utcnow()
        )
    
    async def _run_in_executor(self, func, *args):
        """Run CPU-intensive operations in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data using DataCleaner."""
        # Get numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Clean data
        if numerical_cols:
            df = self.data_cleaner.impute_numerical(df, numerical_cols)
        
        if categorical_cols:
            df = self.data_cleaner.impute_categorical(df, categorical_cols)
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features using FeatureEngineer."""
        # Create polynomial features if external sources are available
        if all(col in df.columns for col in self.feature_engineer.ext_source_cols):
            df = self.feature_engineer.create_polynomial_features(df)
        
        # Create domain-specific features if income and credit amount are available
        if 'AMT_INCOME_TOTAL' in df.columns and 'AMT_CREDIT' in df.columns:
            df = self.feature_engineer.create_domain_features(df)
        
        return df
    
    def _calculate_data_quality(self, df: pd.DataFrame, validation_report: ValidationReport) -> DataQuality:
        """Calculate comprehensive data quality metrics."""
        # Completeness: percentage of non-null values
        total_cells = df.size
        non_null_cells = df.count().sum()
        completeness = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
        
        # Consistency: based on validation report
        consistency = 100 - (validation_report.warning_count * 5)  # Deduct 5% per warning
        consistency = max(0, min(100, consistency))
        
        # Accuracy: based on validation errors
        accuracy = 100 - (validation_report.error_count * 10)  # Deduct 10% per error
        accuracy = max(0, min(100, accuracy))
        
        # Timeliness: assume fresh data for now
        timeliness = 100
        
        # Overall score: weighted average
        overall_score = (
            completeness * 0.3 +
            consistency * 0.3 +
            accuracy * 0.3 +
            timeliness * 0.1
        )
        
        # Collect issues
        issues = []
        if completeness < 95:
            issues.append(f"Low completeness: {completeness:.1f}%")
        if validation_report.warning_count > 0:
            issues.append(f"{validation_report.warning_count} validation warnings")
        if validation_report.error_count > 0:
            issues.append(f"{validation_report.error_count} validation errors")
        
        return DataQuality(
            completeness=round(completeness, 2),
            consistency=round(consistency, 2),
            accuracy=round(accuracy, 2),
            timeliness=round(timeliness, 2),
            overall_score=round(overall_score, 2),
            issues=issues
        )
    
    def _update_processing_stats(self, processing_time: float):
        """Update processing statistics."""
        if self.processing_stats["total_requests"] > 0:
            current_avg = self.processing_stats["average_processing_time"]
            count = self.processing_stats["total_requests"]
            
            # Calculate new average
            new_avg = ((current_avg * (count - 1)) + processing_time) / count
            self.processing_stats["average_processing_time"] = round(new_avg, 3)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics."""
        cache_stats = self.cache.get_stats()
        
        return {
            "processing": self.processing_stats,
            "cache": cache_stats,
            "performance": {
                "cache_hit_rate": cache_stats["hit_rate"],
                "average_processing_time": self.processing_stats["average_processing_time"],
                "error_rate": (
                    self.processing_stats["processing_errors"] / 
                    max(1, self.processing_stats["total_requests"]) * 100
                )
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def bulk_process_data(
        self,
        data_batch: List[Dict[str, Any]],
        processing_options: Dict[str, Any] = None
    ) -> List[ProcessedData]:
        """
        Process multiple data records in parallel.
        
        Args:
            data_batch: List of data records to process
            processing_options: Processing configuration
            
        Returns:
            List of ProcessedData objects
        """
        tasks = []
        
        for data_record in data_batch:
            task = self.process_data(
                data_record,
                processing_options=processing_options
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Bulk processing error for record {i}: {result}")
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def cleanup(self):
        """Cleanup resources."""
        if hasattr(self.executor, 'shutdown'):
            self.executor.shutdown(wait=True)


# Global service instance
_data_service_instance = None


def get_data_service() -> EnhancedDataService:
    """Get the global data service instance."""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = EnhancedDataService()
    return _data_service_instance
