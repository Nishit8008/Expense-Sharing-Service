from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "Expense Sharing Service"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./expense_sharing.db"
    DEBUG: bool = False



settings = Settings()
