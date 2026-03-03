from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AI_PROVIDER: str = "ollama"  # openai or ollama
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    AI_MODEL: str = "llama2"
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "coruja_monitor"
    POSTGRES_USER: str = "coruja"
    POSTGRES_PASSWORD: str = "coruja_secure_password"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

settings = Settings()
