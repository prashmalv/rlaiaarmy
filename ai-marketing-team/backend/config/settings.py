from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    MODEL_NAME: str = "claude-sonnet-4-6"

    # RightLeftAI Brand
    BRAND_NAME: str = "RightLeftAI"
    BRAND_WEBSITE: str = "https://rightleft.ai"
    BRAND_TAGLINE: str = "AI Solutions That Think Differently"

    # Email (SMTP or SendGrid)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_NAME: str = "RightLeftAI Team"

    # Social Media API Keys (set these after OAuth)
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_PERSON_URN: str = ""          # urn:li:person:xxx
    LINKEDIN_ORGANIZATION_URN: str = ""    # urn:li:organization:xxx (company page)

    FACEBOOK_PAGE_ACCESS_TOKEN: str = ""
    FACEBOOK_PAGE_ID: str = ""

    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""

    # Image generation (optional)
    OPENAI_API_KEY: str = ""               # For DALL-E image generation
    PEXELS_API_KEY: str = ""               # For Pexels stock photos (free at pexels.com/api)

    # News & Intelligence
    NEWS_API_KEY: str = ""                 # newsapi.org free tier
    SERPER_API_KEY: str = ""               # serper.dev for Google search

    # Database
    DB_URL: str = "sqlite+aiosqlite:///./rlai_marketing.db"

    # Scheduling
    DAILY_POST_TIME: str = "09:00"         # HH:MM UTC
    DAILY_LEADS_SCAN_TIME: str = "07:00"
    DAILY_EMAIL_TIME: str = "10:00"

    # Approval mode: "auto" posts directly, "manual" waits for approval
    POSTING_MODE: str = "manual"

    class Config:
        env_file = ".env"

settings = Settings()
