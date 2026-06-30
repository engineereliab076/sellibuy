"""Central configuration module.

Loads all environment variables from .env via Pydantic Settings and exposes
a single ``settings`` instance for use across the application.
"""

from pydantic import PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=True,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Database — DigitalOcean Managed PostgreSQL
    # -------------------------------------------------------------------------
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 7  # Per-process; see Appendix A §A.2

    # -------------------------------------------------------------------------
    # Redis — DigitalOcean Managed Redis
    # -------------------------------------------------------------------------
    REDIS_URL: RedisDsn
    REDIS_SESSION_PREFIX: str = "session:"
    REDIS_CACHE_PREFIX: str = "cache:"
    REDIS_RATE_LIMIT_PREFIX: str = "ratelimit:"

    # -------------------------------------------------------------------------
    # Authentication & Security
    # -------------------------------------------------------------------------
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_EXPIRY: str = "15m"
    JWT_REFRESH_EXPIRY: str = "30d"

    # -------------------------------------------------------------------------
    # Payment Gateway — DPO Group
    # -------------------------------------------------------------------------
    DPO_COMPANY_TOKEN: str
    DPO_SECRET: str  # HMAC-SHA512 webhook verification key
    DPO_SANDBOX: bool = True
    DPO_API_URL: str = "https://secure.3gdirectpay.com"
    DPO_PAYMENT_URL: str = "https://pay.dpogroup.com"

    # -------------------------------------------------------------------------
    # SMS — Africa's Talking
    # -------------------------------------------------------------------------
    AFRICATALKING_KEY: str
    AFRICATALKING_USERNAME: str
    AFRICATALKING_SENDER_ID: str = "SELLIBUY"

    # -------------------------------------------------------------------------
    # WhatsApp — Business API
    # -------------------------------------------------------------------------
    WHATSAPP_API_KEY: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""

    # -------------------------------------------------------------------------
    # Email — SendGrid
    # -------------------------------------------------------------------------
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str = "noreply@sellibuy.co.tz"
    SENDGRID_FROM_NAME: str = "SelliBuy"

    # -------------------------------------------------------------------------
    # File Storage — AWS S3 + CloudFront
    # -------------------------------------------------------------------------
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str
    AWS_CLOUDFRONT_DOMAIN: str = "https://cdn.sellibuy.co.tz"
    AWS_S3_PRESIGN_EXPIRY: int = 900  # Seconds; 15 minutes

    # -------------------------------------------------------------------------
    # Monitoring & Error Tracking
    # -------------------------------------------------------------------------
    SENTRY_DSN: str = ""
    PROMETHEUS_ENDPOINT: str = ""
    GRAFANA_URL: str = ""

    # -------------------------------------------------------------------------
    # Infrastructure — Cloudflare
    # -------------------------------------------------------------------------
    CLOUDFLARE_API_KEY: str = ""
    CLOUDFLARE_ZONE_ID: str = ""

    # -------------------------------------------------------------------------
    # Background Jobs — Celery
    # -------------------------------------------------------------------------
    CELERY_BROKER_URL: str = ""  # Derived from REDIS_URL if not set explicitly
    CELERY_RESULT_EXPIRES: int = 86400  # 24 hours in seconds

    # Scheduled job intervals (seconds)
    ORDER_EXPIRY_SWEEP_INTERVAL: int = 3600
    AUTO_COMPLETE_SWEEP_INTERVAL: int = 3600
    DISPUTE_ESCALATE_SWEEP_INTERVAL: int = 3600
    ORPHAN_FILE_CLEANUP_INTERVAL: int = 86400

    # Business rule durations
    ORDER_EXPIRY_HOURS: int = 24
    AUTO_COMPLETE_DAYS: int = 7
    DISPUTE_ESCALATE_DAYS: int = 14

    # -------------------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------------------
    ENABLE_WHATSAPP: bool = False
    ENABLE_OFFLINE_SYNC: bool = True
    ENABLE_AUTO_COMPLETE: bool = True
    ENABLE_SUPPLIER_CSV: bool = False
    ENABLE_AGENT_DISTANCE_SORT: bool = False

    # -------------------------------------------------------------------------
    # Offline Sync — Agent App (Expo)
    # -------------------------------------------------------------------------
    EXPO_API_BASE_URL: str = "https://api.sellibuy.co.tz"
    EXPO_SYNC_RETRY_ATTEMPTS: int = 5
    EXPO_SYNC_RETRY_BACKOFF_MS: int = 2000
    EXPO_OFFLINE_STORAGE_WARNING_MB: int = 100

    @model_validator(mode="after")
    def derive_celery_broker_url(self) -> Settings:
        """Fall back to REDIS_URL when CELERY_BROKER_URL is not explicitly set."""
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = str(self.REDIS_URL)
        return self


settings = Settings()
