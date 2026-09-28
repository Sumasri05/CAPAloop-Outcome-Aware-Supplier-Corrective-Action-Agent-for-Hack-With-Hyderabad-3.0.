"""
CAPAloop — Learning timeline API.

GET /api/learning/timeline
"""

from __future__ import annotations

from fastapi import APIRouter

from ..models import TimelineResponse
from ..services.timeline import get_timeline

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/timeline", response_model=TimelineResponse)
async def timeline() -> TimelineResponse:
    """Return the learning timeline, newest events first."""
    events = get_timeline()
    return TimelineResponse(events=events, total=len(events))
