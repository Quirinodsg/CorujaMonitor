"""E2E test conftest — patches config for api imports."""
import sys, os, types

# Only add api/ to path if not already there and config not already mocked
api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

class _S:
    POSTGRES_HOST="localhost"; POSTGRES_PORT=5432; POSTGRES_DB="test"
    POSTGRES_USER="test"; POSTGRES_PASSWORD="test"
    SECRET_KEY="test-key"; JWT_ALGORITHM="HS256"; JWT_EXPIRATION_MINUTES=1440
    REDIS_HOST="localhost"; REDIS_PORT=6379; AI_PROVIDER="openai"
    OPENAI_API_KEY=""; AI_AGENT_URL="http://localhost:8001"
    PROBE_TOKEN_EXPIRATION_DAYS=365; DATABASE_URL="sqlite:///:memory:"

if 'config' not in sys.modules:
    m = types.ModuleType('config'); m.settings = _S(); m.Settings = type(_S)
    sys.modules['config'] = m

if api_path not in sys.path:
    sys.path.append(api_path)  # append instead of insert to avoid shadowing
