"""
Configuration management utilities.

This module provides configuration management for the credit risk model,
including environment variables, database settings, and model parameters.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "credit_risk_db"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"


@dataclass
class RedisConfig:
    """Redis configuration settings."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    
    @property
    def connection_string(self) -> str:
        """Get Redis connection string."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"


@dataclass
class MLflowConfig:
    """MLflow configuration settings."""
    tracking_uri: str = "file:./mlruns"
    experiment_name: str = "credit_risk_model"
    model_name: str = "credit_risk_lightgbm"
    model_stage: str = "Production"
    artifact_location: Optional[str] = None


@dataclass
class ModelConfig:
    """Model configuration settings."""
    random_state: int = 42
    test_size: float = 0.2
    validation_size: float = 0.2
    cv_folds: int = 5
    early_stopping_rounds: int = 50
    
    # LightGBM specific
    lgb_n_estimators: int = 1000
    lgb_num_leaves: int = 31
    lgb_learning_rate: float = 0.01
    lgb_subsample: float = 0.8
    lgb_colsample_bytree: float = 0.8
    lgb_min_child_samples: int = 20
    
    # XGBoost specific
    xgb_n_estimators: int = 1000
    xgb_max_depth: int = 7
    xgb_learning_rate: float = 0.01
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8
    xgb_min_child_weight: int = 1


@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    log_level: str = "info"
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class AAConfig:
    """Account Aggregator configuration settings."""
    base_url: str = "https://api.sahamati.org.in"
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8000/callback"
    consent_duration_days: int = 90
    data_fetch_timeout: int = 300
    max_retry_attempts: int = 3


class Config:
    """Main configuration class."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and config file."""
        # Load from config file if provided
        file_config = {}
        if self.config_file and Path(self.config_file).exists():
            file_config = self._load_config_file(self.config_file)
        
        # Database configuration
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", file_config.get("database", {}).get("host", "localhost")),
            port=int(os.getenv("DB_PORT", file_config.get("database", {}).get("port", 5432))),
            database=os.getenv("DB_NAME", file_config.get("database", {}).get("database", "credit_risk_db")),
            username=os.getenv("DB_USER", file_config.get("database", {}).get("username", "postgres")),
            password=os.getenv("DB_PASSWORD", file_config.get("database", {}).get("password", "")),
            ssl_mode=os.getenv("DB_SSL_MODE", file_config.get("database", {}).get("ssl_mode", "prefer"))
        )
        
        # Redis configuration
        self.redis = RedisConfig(
            host=os.getenv("REDIS_HOST", file_config.get("redis", {}).get("host", "localhost")),
            port=int(os.getenv("REDIS_PORT", file_config.get("redis", {}).get("port", 6379))),
            database=int(os.getenv("REDIS_DB", file_config.get("redis", {}).get("database", 0))),
            password=os.getenv("REDIS_PASSWORD", file_config.get("redis", {}).get("password"))
        )
        
        # MLflow configuration
        self.mlflow = MLflowConfig(
            tracking_uri=os.getenv("MLFLOW_TRACKING_URI", file_config.get("mlflow", {}).get("tracking_uri", "file:./mlruns")),
            experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME", file_config.get("mlflow", {}).get("experiment_name", "credit_risk_model")),
            model_name=os.getenv("MLFLOW_MODEL_NAME", file_config.get("mlflow", {}).get("model_name", "credit_risk_lightgbm")),
            model_stage=os.getenv("MLFLOW_MODEL_STAGE", file_config.get("mlflow", {}).get("model_stage", "Production")),
            artifact_location=os.getenv("MLFLOW_ARTIFACT_LOCATION", file_config.get("mlflow", {}).get("artifact_location"))
        )
        
        # Model configuration
        model_config = file_config.get("model", {})
        self.model = ModelConfig(
            random_state=int(os.getenv("MODEL_RANDOM_STATE", model_config.get("random_state", 42))),
            test_size=float(os.getenv("MODEL_TEST_SIZE", model_config.get("test_size", 0.2))),
            validation_size=float(os.getenv("MODEL_VALIDATION_SIZE", model_config.get("validation_size", 0.2))),
            cv_folds=int(os.getenv("MODEL_CV_FOLDS", model_config.get("cv_folds", 5))),
            early_stopping_rounds=int(os.getenv("MODEL_EARLY_STOPPING", model_config.get("early_stopping_rounds", 50)))
        )
        
        # API configuration
        api_config = file_config.get("api", {})
        self.api = APIConfig(
            host=os.getenv("API_HOST", api_config.get("host", "0.0.0.0")),
            port=int(os.getenv("API_PORT", api_config.get("port", 8000))),
            debug=os.getenv("API_DEBUG", str(api_config.get("debug", False))).lower() == "true",
            reload=os.getenv("API_RELOAD", str(api_config.get("reload", False))).lower() == "true",
            workers=int(os.getenv("API_WORKERS", api_config.get("workers", 1))),
            log_level=os.getenv("API_LOG_LEVEL", api_config.get("log_level", "info")),
            cors_origins=os.getenv("API_CORS_ORIGINS", "").split(",") if os.getenv("API_CORS_ORIGINS") else api_config.get("cors_origins", ["*"])
        )
        
        # Account Aggregator configuration
        aa_config = file_config.get("account_aggregator", {})
        self.aa = AAConfig(
            base_url=os.getenv("AA_BASE_URL", aa_config.get("base_url", "https://api.sahamati.org.in")),
            client_id=os.getenv("AA_CLIENT_ID", aa_config.get("client_id", "")),
            client_secret=os.getenv("AA_CLIENT_SECRET", aa_config.get("client_secret", "")),
            redirect_uri=os.getenv("AA_REDIRECT_URI", aa_config.get("redirect_uri", "http://localhost:8000/callback")),
            consent_duration_days=int(os.getenv("AA_CONSENT_DURATION", aa_config.get("consent_duration_days", 90))),
            data_fetch_timeout=int(os.getenv("AA_DATA_TIMEOUT", aa_config.get("data_fetch_timeout", 300))),
            max_retry_attempts=int(os.getenv("AA_MAX_RETRIES", aa_config.get("max_retry_attempts", 3)))
        )
        
        # Application paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.models_dir = self.project_root / "models"
        self.logs_dir = self.project_root / "logs"
        
        # Create directories if they don't exist
        for directory in [self.data_dir, self.models_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from YAML or JSON file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Dictionary containing configuration data
        """
        config_path = Path(config_file)
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif config_path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    logger.warning(f"Unsupported config file format: {config_path.suffix}")
                    return {}
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'database': asdict(self.database),
            'redis': asdict(self.redis),
            'mlflow': asdict(self.mlflow),
            'model': asdict(self.model),
            'api': asdict(self.api),
            'aa': asdict(self.aa),
            'paths': {
                'project_root': str(self.project_root),
                'data_dir': str(self.data_dir),
                'models_dir': str(self.models_dir),
                'logs_dir': str(self.logs_dir)
            }
        }
    
    def save_config(self, output_file: str):
        """
        Save current configuration to file.
        
        Args:
            output_file: Path to output configuration file
        """
        config_dict = self.to_dict()
        output_path = Path(output_file)
        
        try:
            with open(output_path, 'w') as f:
                if output_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.safe_dump(config_dict, f, default_flow_style=False, indent=2)
                elif output_path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2, default=str)
                else:
                    raise ValueError(f"Unsupported output format: {output_path.suffix}")
            
            logger.info(f"Configuration saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving config to {output_file}: {e}")
            raise


# Global configuration instance
config = Config()


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Global configuration instance
    """
    return config


def reload_config(config_file: Optional[str] = None) -> Config:
    """
    Reload the global configuration.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Reloaded configuration instance
    """
    global config
    config = Config(config_file)
    return config
