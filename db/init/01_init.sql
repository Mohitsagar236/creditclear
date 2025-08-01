-- Initialize Credit Risk Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table for application users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create credit applications table
CREATE TABLE IF NOT EXISTS credit_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    application_data JSONB NOT NULL,
    risk_score DECIMAL(5,4),
    risk_category VARCHAR(20),
    model_version VARCHAR(50),
    prediction_confidence DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create prediction history table
CREATE TABLE IF NOT EXISTS prediction_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES credit_applications(id),
    task_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create model metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_path VARCHAR(255),
    metrics JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_name, model_version)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_credit_applications_user_id ON credit_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_applications_created_at ON credit_applications(created_at);
CREATE INDEX IF NOT EXISTS idx_prediction_history_application_id ON prediction_history(application_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_task_id ON prediction_history(task_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_status ON prediction_history(status);
CREATE INDEX IF NOT EXISTS idx_model_metadata_active ON model_metadata(is_active);

-- Insert default admin user
INSERT INTO users (username, email) VALUES 
    ('admin', 'admin@creditrisk.local')
ON CONFLICT (username) DO NOTHING;

-- Insert sample model metadata
INSERT INTO model_metadata (model_name, model_version, model_path, is_active, metrics) VALUES 
    ('xgboost_model', 'v1.0', '/app/data/models/xgboost_model.pkl', TRUE, '{"accuracy": 0.85, "precision": 0.82, "recall": 0.88}'),
    ('lightgbm_model', 'v1.0', '/app/data/models/lightgbm_model.pkl', FALSE, '{"accuracy": 0.87, "precision": 0.84, "recall": 0.86}')
ON CONFLICT (model_name, model_version) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credit_applications_updated_at BEFORE UPDATE ON credit_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
