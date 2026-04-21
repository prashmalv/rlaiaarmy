from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    MODEL_NAME: str = "claude-sonnet-4-6"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    APPROVAL_EMAIL: str = ""

    DB_URL: str = "sqlite+aiosqlite:///./ai_dev_team.db"

    SPRINT_DURATION_MINUTES: int = 120  # 2 hours
    MAX_ENGINEERS: int = 3
    MAX_FULLSTACK_DEVS: int = 3

    OUTPUT_DIR: str = "./generated_projects"
    REPORTS_DIR: str = "./reports_output"

    class Config:
        env_file = ".env"

settings = Settings()
