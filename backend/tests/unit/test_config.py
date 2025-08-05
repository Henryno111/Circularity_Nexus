"""
Unit tests for configuration module
"""

import pytest
from unittest.mock import patch
from pydantic import ValidationError

from circularity_nexus.core.config import Settings


class TestSettings:
    """Test cases for Settings configuration"""
    
    def test_default_settings(self):
        """Test default settings values"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key'
        }):
            settings = Settings()
            
            assert settings.APP_NAME == "Circularity Nexus API"
            assert settings.APP_VERSION == "1.0.0"
            assert settings.DEBUG is False
            assert settings.ENVIRONMENT == "production"
            assert settings.API_V1_STR == "/api/v1"
            assert settings.HOST == "0.0.0.0"
            assert settings.PORT == 8000
    
    def test_cors_origins_parsing(self):
        """Test CORS origins string parsing"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'CORS_ORIGINS': 'http://localhost:3000,https://app.example.com,http://localhost:8080'
        }):
            settings = Settings()
            
            expected_origins = [
                'http://localhost:3000',
                'https://app.example.com',
                'http://localhost:8080'
            ]
            assert settings.CORS_ORIGINS == expected_origins
    
    def test_allowed_extensions_parsing(self):
        """Test allowed extensions string parsing"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'ALLOWED_EXTENSIONS': '.jpg,.png,.gif,.bmp'
        }):
            settings = Settings()
            
            expected_extensions = ['.jpg', '.png', '.gif', '.bmp']
            assert settings.ALLOWED_EXTENSIONS == expected_extensions
    
    def test_groq_configuration(self):
        """Test Groq AI configuration"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'GROQ_API_KEY': 'test-groq-key',
            'GROQ_MODEL': 'llama3-70b-8192'
        }):
            settings = Settings()
            
            assert settings.GROQ_API_KEY == 'test-groq-key'
            assert settings.GROQ_MODEL == 'llama3-70b-8192'
            assert settings.GROQ_BASE_URL == 'https://api.groq.com/openai/v1'
    
    def test_ai_configuration(self):
        """Test AI processing configuration"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'AI_CONFIDENCE_THRESHOLD': '0.9',
            'AI_BATCH_SIZE': '64',
            'AI_MAX_IMAGE_SIZE': '2048'
        }):
            settings = Settings()
            
            assert settings.AI_CONFIDENCE_THRESHOLD == 0.9
            assert settings.AI_BATCH_SIZE == 64
            assert settings.AI_MAX_IMAGE_SIZE == 2048
    
    def test_database_configuration(self):
        """Test database configuration"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./custom.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'DATABASE_ECHO': 'true',
            'DATABASE_POOL_SIZE': '10'
        }):
            settings = Settings()
            
            assert settings.DATABASE_URL == 'sqlite+aiosqlite:///./custom.db'
            assert settings.DATABASE_ECHO is True
            assert settings.DATABASE_POOL_SIZE == 10
    
    def test_hedera_configuration(self):
        """Test Hedera blockchain configuration"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_NETWORK': 'mainnet',
            'HEDERA_ACCOUNT_ID': '0.0.789012',
            'HEDERA_PRIVATE_KEY': 'mainnet-private-key',
            'HEDERA_PUBLIC_KEY': 'mainnet-public-key'
        }):
            settings = Settings()
            
            assert settings.HEDERA_NETWORK == 'mainnet'
            assert settings.HEDERA_ACCOUNT_ID == '0.0.789012'
            assert settings.HEDERA_PRIVATE_KEY == 'mainnet-private-key'
            assert settings.HEDERA_PUBLIC_KEY == 'mainnet-public-key'
    
    def test_required_fields_validation(self):
        """Test validation of required fields"""
        # Test missing SECRET_KEY
        with patch.dict('os.environ', {
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key'
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert 'SECRET_KEY' in str(exc_info.value)
    
    def test_secret_key_length_validation(self):
        """Test SECRET_KEY minimum length validation"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'short',  # Too short
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key'
        }):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert 'at least 32 characters' in str(exc_info.value)
    
    def test_upload_dir_creation(self):
        """Test upload directory creation"""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_path = os.path.join(temp_dir, 'test_uploads')
            
            with patch.dict('os.environ', {
                'SECRET_KEY': 'test-secret-key-32-characters-long',
                'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
                'HEDERA_ACCOUNT_ID': '0.0.123456',
                'HEDERA_PRIVATE_KEY': 'test-private-key',
                'HEDERA_PUBLIC_KEY': 'test-public-key',
                'UPLOAD_DIR': upload_path
            }):
                settings = Settings()
                
                assert settings.UPLOAD_DIR == upload_path
                assert os.path.exists(upload_path)
    
    def test_development_vs_production_settings(self):
        """Test different settings for development vs production"""
        # Development settings
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./test.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'test-private-key',
            'HEDERA_PUBLIC_KEY': 'test-public-key',
            'DEBUG': 'true',
            'ENVIRONMENT': 'development',
            'RELOAD': 'true',
            'WORKERS': '1'
        }):
            dev_settings = Settings()
            
            assert dev_settings.DEBUG is True
            assert dev_settings.ENVIRONMENT == 'development'
            assert dev_settings.RELOAD is True
            assert dev_settings.WORKERS == 1
        
        # Production settings
        with patch.dict('os.environ', {
            'SECRET_KEY': 'production-secret-key-32-characters-long',
            'DATABASE_URL': 'sqlite+aiosqlite:///./prod.db',
            'HEDERA_ACCOUNT_ID': '0.0.123456',
            'HEDERA_PRIVATE_KEY': 'prod-private-key',
            'HEDERA_PUBLIC_KEY': 'prod-public-key',
            'DEBUG': 'false',
            'ENVIRONMENT': 'production',
            'RELOAD': 'false',
            'WORKERS': '4'
        }):
            prod_settings = Settings()
            
            assert prod_settings.DEBUG is False
            assert prod_settings.ENVIRONMENT == 'production'
            assert prod_settings.RELOAD is False
            assert prod_settings.WORKERS == 4
