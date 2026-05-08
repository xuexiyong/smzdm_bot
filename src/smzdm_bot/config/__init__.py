"""Configuration management for SMZDM Bot.

Configuration is loaded from environment variables using Pydantic Settings.

Environment Variables:
    SMZDM_COOKIE: Cookie string (single user mode)
    SMZDM_SK: Optional security key
    SMZDM_USERS: JSON array for multi-user mode
        Example: '[{"cookie": "...", "sk": "..."}, {"cookie": "..."}]'

    Notification:
    SMZDM_PUSH_PLUS_TOKEN: PushPlus token
    SMZDM_SC_KEY: ServerChan key
    SMZDM_WECOM_WEBHOOK: WeCom bot webhook URL
    SMZDM_TG_BOT_TOKEN: Telegram bot token
    SMZDM_TG_USER_ID: Telegram user/chat ID
    SMZDM_TG_TOPIC_ID: Telegram topic/thread ID
    SMZDM_TG_API_BASE: Custom Telegram API base URL

    Scheduler:
    SMZDM_SCH_HOUR: Hour to run (0-23)
    SMZDM_SCH_MINUTE: Minute to run (0-59)
    SMZDM_TIMEZONE: Timezone (default: Asia/Shanghai)
"""

import json
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from smzdm_bot.exceptions import ConfigurationError


def _find_dotenv() -> Path | None:
    """Find .env file by searching up from cwd or using package location."""
    cwd = Path.cwd()
    if (cwd / ".env").exists():
        return cwd / ".env"

    pkg_dir = Path(__file__).parent.parent.parent.parent
    if (pkg_dir / ".env").exists():
        return pkg_dir / ".env"

    return None


class UserConfig(BaseModel):
    """Configuration for a single user account.

    Attributes:
        cookie: SMZDM cookie string.
        sk: Optional security key from app.
        name: Optional user identifier for logging.
    """

    cookie: str
    sk: str = ""
    name: str = ""

    @field_validator("cookie")
    @classmethod
    def validate_cookie(cls, v: str) -> str:
        """Ensure cookie is not empty."""
        if not v or not v.strip():
            raise ValueError("Cookie cannot be empty")
        return v.strip()


class NotifyConfig(BaseModel):
    """Notification service configuration.

    All fields are optional. Leave empty to disable a provider.
    """

    push_plus_token: str = ""
    sc_key: str = ""
    wecom_webhook: str = ""
    tg_bot_token: str = ""
    tg_user_id: str = ""
    tg_topic_id: str = ""
    tg_api_base: str = ""

    @property
    def has_any_provider(self) -> bool:
        """Check if at least one notification provider is configured."""
        return any(
            [
                self.push_plus_token,
                self.sc_key,
                self.wecom_webhook,
                self.tg_bot_token and self.tg_user_id,
            ]
        )


class SchedulerConfig(BaseModel):
    """Scheduler configuration."""

    hour: int | None = None
    minute: int | None = None
    timezone: str = "Asia/Shanghai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses SMZDM_ prefix for all environment variables.

    Example:
        export SMZDM_COOKIE="your_cookie_here"
        export SMZDM_PUSH_PLUS_TOKEN="your_token"
