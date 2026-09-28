"""
CAPAloop — Configuration module.

Loads Hindsight Cloud connection parameters from environment variables.
Uses python-dotenv to read from a .env file when present.
Never logs or exposes the API key.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Walk up from backend/app/ to project root to find .env
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class HindsightSettings(BaseModel):
    """Validated settings for the Hindsight Cloud connection."""

    api_url: str = Field(
        ...,
        min_length=1,
        description="Base URL of the Hindsight Cloud API.",
    )
    api_key: str = Field(
        ...,
        min_length=1,
        description="API key for Hindsight Cloud authentication.",
    )
    bank_id: str = Field(
        ...,
        min_length=1,
        description="Memory bank identifier for CAPAloop experiences.",
    )


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


def load_settings() -> HindsightSettings:
    """Load and validate Hindsight settings from environment variables.

    Returns:
        HindsightSettings with validated values.

    Raises:
        ConfigurationError: If required variables are missing or invalid.
    """
    try:
        return HindsightSettings(
            api_url=os.getenv("HINDSIGHT_API_URL", ""),
            api_key=os.getenv("HINDSIGHT_API_KEY", ""),
            bank_id=os.getenv("HINDSIGHT_BANK_ID", ""),
        )
    except ValidationError as exc:
        missing = [
            e["loc"][0]
            for e in exc.errors()
            if e["type"] == "string_too_short"
        ]
        raise ConfigurationError(
            f"Missing or empty Hindsight configuration: {', '.join(missing)}. "
            "Ensure HINDSIGHT_API_URL, HINDSIGHT_API_KEY, and "
            "HINDSIGHT_BANK_ID are set in the environment or .env file."
        ) from exc
