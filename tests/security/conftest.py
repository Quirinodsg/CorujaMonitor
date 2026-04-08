"""
Security test conftest — patches config to avoid .env validation errors.
"""
import sys
import os
import types
from unittest.mock import MagicMock

api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'api'))
if api_path not in sys.path:
    sys.path.append(api_path)

class _MockSettings:
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5432
    POSTGRES_DB = "test"
    POSTGRES_USER = "test"
    POSTGRES_PASSWORD = "test"
    SECRET_KEY = "test-secret-key-for-jwt"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_MINUTES = 1440
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    AI_PROVIDER = "openai"
    OPENAI_API_KEY = ""
    AI_AGENT_URL = "http://localhost:8001"
    PROBE_TOKEN_EXPIRATION_DAYS = 365
    DATABASE_URL = "sqlite:///:memory:"

if 'config' not in sys.modules:
    config_module = types.ModuleType('config')
    config_module.settings = _MockSettings()
    config_module.Settings = type(_MockSettings)
    sys.modules['config'] = config_module
