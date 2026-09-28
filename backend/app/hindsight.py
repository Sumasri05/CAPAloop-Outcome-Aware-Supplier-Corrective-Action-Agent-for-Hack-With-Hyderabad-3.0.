"""
CAPAloop — Hindsight Cloud client wrapper.

Provides retain / recall / reflect methods that delegate to the
official hindsight-client SDK.  All errors are surfaced as typed
exceptions so the FastAPI layer can return safe, informative responses.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from hindsight_client import Hindsight

from .config import HindsightSettings, ConfigurationError, load_settings

logger = logging.getLogger("capaloop.hindsight")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class HindsightError(Exception):
    """Base class for Hindsight-related errors."""


class HindsightAuthError(HindsightError):
    """Raised when the API key is rejected."""


class HindsightBankError(HindsightError):
    """Raised when the memory bank is inaccessible."""


class HindsightConnectionError(HindsightError):
    """Raised when the Hindsight API is unreachable."""


class HindsightRetainError(HindsightError):
    """Raised when a retain operation fails."""


class HindsightRecallError(HindsightError):
    """Raised when a recall operation fails."""


class HindsightReflectError(HindsightError):
    """Raised when a reflect operation fails."""


# ---------------------------------------------------------------------------
# Response containers
# ---------------------------------------------------------------------------

@dataclass
class RetainResult:
    """Result of a successful retain operation."""
    success: bool
    detail: str = ""
    raw: Any = field(default=None, repr=False)


@dataclass
class RecallResult:
    """Result of a successful recall operation."""
    results: list[str] = field(default_factory=list)
    raw: Any = field(default=None, repr=False)


@dataclass
class ReflectResult:
    """Result of a successful reflect operation."""
    text: str = ""
    raw: Any = field(default=None, repr=False)


# ---------------------------------------------------------------------------
# Client wrapper
# ---------------------------------------------------------------------------

class HindsightClient:
    """Thin wrapper around the official Hindsight Python SDK."""

    def __init__(self, settings: HindsightSettings | None = None) -> None:
        if settings is None:
            settings = load_settings()          # may raise ConfigurationError
        self._settings = settings
        self._bank_id = settings.bank_id
        logger.info(
            "Initialising Hindsight client (url=%s, bank=%s)",
            settings.api_url,
            self._bank_id,
        )
        try:
            self._client = Hindsight(
                base_url=settings.api_url,
                api_key=settings.api_key,
            )
        except Exception as exc:
            raise HindsightConnectionError(
                f"Failed to initialise Hindsight client: {exc}"
            ) from exc

    # -- Retain -------------------------------------------------------------

    def retain(self, content: str) -> RetainResult:
        """Store an experience in the configured memory bank.

        Args:
            content: Free-text representation of the experience.

        Returns:
            RetainResult confirming success.

        Raises:
            HindsightRetainError: If the API rejects the request.
            HindsightAuthError: On authentication failure.
            HindsightConnectionError: On network issues.
        """
        try:
            response = self._client.retain(
                bank_id=self._bank_id,
                content=content,
            )
            logger.info("Retain succeeded for bank=%s", self._bank_id)
            return RetainResult(success=True, detail="retained", raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "retain", HindsightRetainError)
            # The above always raises; this line satisfies the type checker.
            raise  # pragma: no cover

    async def aretain(self, content: str) -> RetainResult:
        """Store an experience asynchronously (safe inside FastAPI Tasks)."""
        try:
            response = await self._client.aretain(
                bank_id=self._bank_id,
                content=content,
            )
            logger.info("Async retain succeeded for bank=%s", self._bank_id)
            return RetainResult(success=True, detail="retained", raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "retain", HindsightRetainError)
            raise

    # -- Recall -------------------------------------------------------------

    def recall(self, query: str) -> RecallResult:
        """Search for relevant historical experiences.

        Args:
            query: Natural-language search query.

        Returns:
            RecallResult with matching memory snippets (may be empty).

        Raises:
            HindsightRecallError: If the API rejects the request.
        """
        try:
            response = self._client.recall(
                bank_id=self._bank_id,
                query=query,
            )
            # The SDK returns an object with a .results list.
            # Extract text from each result, handling both str and object forms.
            results: list[str] = []
            raw_results = getattr(response, "results", None) or []
            for item in raw_results:
                if isinstance(item, str):
                    results.append(item)
                else:
                    # Some SDK versions return objects with .content / .text
                    text = getattr(item, "content", None) or getattr(item, "text", None) or str(item)
                    results.append(text)
            logger.info(
                "Recall returned %d result(s) for bank=%s",
                len(results),
                self._bank_id,
            )
            return RecallResult(results=results, raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "recall", HindsightRecallError)
            raise  # pragma: no cover

    async def arecall(self, query: str) -> RecallResult:
        """Search for relevant historical experiences asynchronously."""
        try:
            response = await self._client.arecall(
                bank_id=self._bank_id,
                query=query,
            )
            results: list[str] = []
            raw_results = getattr(response, "results", None) or []
            for item in raw_results:
                if isinstance(item, str):
                    results.append(item)
                else:
                    text = getattr(item, "content", None) or getattr(item, "text", None) or str(item)
                    results.append(text)
            logger.info(
                "Async recall returned %d result(s) for bank=%s",
                len(results),
                self._bank_id,
            )
            return RecallResult(results=results, raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "recall", HindsightRecallError)
            raise

    # -- Reflect ------------------------------------------------------------

    def reflect(self, query: str) -> ReflectResult:
        """Synthesise reasoning over stored experiences.

        Args:
            query: Natural-language prompt for reflection.

        Returns:
            ReflectResult with the synthesised text.

        Raises:
            HindsightReflectError: If the API rejects the request.
        """
        try:
            response = self._client.reflect(
                bank_id=self._bank_id,
                query=query,
            )
            # Response may be a string or an object with .text
            text = response if isinstance(response, str) else getattr(response, "text", str(response))
            logger.info("Reflect succeeded for bank=%s", self._bank_id)
            return ReflectResult(text=text, raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "reflect", HindsightReflectError)
            raise  # pragma: no cover

    async def areflect(self, query: str) -> ReflectResult:
        """Synthesise reasoning over stored experiences asynchronously."""
        try:
            response = await self._client.areflect(
                bank_id=self._bank_id,
                query=query,
            )
            text = response if isinstance(response, str) else getattr(response, "text", str(response))
            logger.info("Async reflect succeeded for bank=%s", self._bank_id)
            return ReflectResult(text=text, raw=response)
        except Exception as exc:
            self._classify_and_raise(exc, "reflect", HindsightReflectError)
            raise

    # -- Health probe -------------------------------------------------------

    def check_connection(self) -> bool:
        """Lightweight connectivity check.

        Attempts a minimal recall to verify authentication and bank access.
        Returns True on success, raises on failure.
        """
        try:
            self._client.recall(bank_id=self._bank_id, query="ping")
            return True
        except Exception as exc:
            self._classify_and_raise(exc, "health-check", HindsightConnectionError)
            raise  # pragma: no cover

    async def acheck_connection(self) -> bool:
        """Lightweight async connectivity check."""
        try:
            await self._client.arecall(bank_id=self._bank_id, query="ping")
            return True
        except Exception as exc:
            self._classify_and_raise(exc, "health-check", HindsightConnectionError)
            raise

    # -- Internal helpers ---------------------------------------------------

    def _classify_and_raise(
        self,
        exc: Exception,
        operation: str,
        default_cls: type[HindsightError],
    ) -> None:
        """Inspect an exception and re-raise as the appropriate typed error."""
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "auth" in msg or "forbidden" in msg or "403" in msg:
            raise HindsightAuthError(
                f"Hindsight authentication failed during {operation}. "
                "Check your HINDSIGHT_API_KEY."
            ) from exc
        if "404" in msg or "not found" in msg:
            raise HindsightBankError(
                f"Hindsight bank '{self._bank_id}' not found during {operation}. "
                "Check your HINDSIGHT_BANK_ID."
            ) from exc
        if "connect" in msg or "timeout" in msg or "unreachable" in msg or "dns" in msg:
            raise HindsightConnectionError(
                f"Could not reach Hindsight API during {operation}: {exc}"
            ) from exc
        # Fallback
        raise default_cls(
            f"Hindsight {operation} failed: {exc}"
        ) from exc
