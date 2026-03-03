from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "coruja_monitor"
    POSTGRES_USER: str = "coruja"
    POSTGRES_PASSWORD: str = "coruja_secure_password"
    
    # Security
    SECRET_KEY: str = "change-this-to-a-secure-random-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # AI
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    AI_AGENT_URL: str = "http://ai-agent:8001"
    
    # Probe
    PROBE_TOKEN_EXPIRATION_DAYS: int = 365
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

settings = Settings()
