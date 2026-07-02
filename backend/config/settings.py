from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Autonomous Multi-Agent Research System"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    TAVILY_API_KEY: str

    MAX_SUB_QUESTIONS: int = 5
    MAX_REVISIONS: int = 3

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "research_agent"

    SQLITE_DB: str = "metrics.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()