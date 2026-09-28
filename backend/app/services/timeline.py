"""
CAPAloop — Learning timeline service.

Maintains an in-memory timeline of learning events (defect analyses,
outcome recordings, experience retentions).

Phase 2 uses in-memory storage only — no database.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock

from ..models import TimelineEvent

logger = logging.getLogger("capaloop.timeline")

_timeline: list[TimelineEvent] = []
_lock = Lock()


def add_event(
    event_type: str,
    experience_id: str,
    summary: str,
) -> TimelineEvent:
    """Record a learning event on the timeline."""
    event = TimelineEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_type,
        experience_id=experience_id,
        summary=summary,
    )
    with _lock:
        _timeline.append(event)
    logger.info("Timeline event: %s — %s", event_type, experience_id)
    return event


def get_timeline() -> list[TimelineEvent]:
    """Return all timeline events, newest first."""
    with _lock:
        return list(reversed(_timeline))


def clear_timeline() -> None:
    """Clear all timeline events (for testing)."""
    with _lock:
        _timeline.clear()
