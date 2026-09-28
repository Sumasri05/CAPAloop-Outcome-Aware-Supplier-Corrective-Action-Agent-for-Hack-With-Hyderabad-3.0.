"""
CAPAloop — Defect analysis API.

POST /api/defects/analyze
"""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from ..hindsight import (
    HindsightAuthError,
    HindsightBankError,
    HindsightConnectionError,
    HindsightError,
)
from ..models import (
    AnalysisResponse,
    DefectInput,
    OutcomeInput,
    OutcomeResponse,
    TimelineResponse,
)
from ..services.recommendations import aanalyze_defect, analyze_defect
from ..services.timeline import add_event, get_timeline
from .experiences import record_outcome as exp_record_outcome, register_pending_experience

logger = logging.getLogger("capaloop.api.defects")

router = APIRouter(prefix="/api/defects", tags=["defects"])


def _get_hindsight_client():
    """Import and retrieve the Hindsight client from main app state."""
    from ..main import _get_client
    return _get_client()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(defect: DefectInput) -> AnalysisResponse:
    """Analyze a new supplier defect using Hindsight recall and reflect.

    Workflow:
      1. Build recall query from defect attributes
      2. Recall similar historical experiences from Hindsight
      3. Analyze historical evidence
      4. Reflect over evidence using Hindsight
      5. Return structured recommendation with evidence and limitations
    """
    client = _get_hindsight_client()

    try:
        result = await aanalyze_defect(defect=defect, client=client)
    except HindsightAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HindsightBankError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HindsightConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HindsightError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Register pending experience so outcome recording retains complete defect context
    register_pending_experience(result.defect_id, defect.model_dump())

    # Record timeline event
    add_event(
        event_type="defect_analyzed",
        experience_id=result.defect_id,
        summary=(
            f"Analyzed {defect.defect_type} on {defect.part_number} "
            f"from {defect.supplier}. "
            f"Evidence grade: {result.recommendation.evidence_grade.value}. "
            f"Historical cases: {result.historical_cases_found}."
        ),
    )

    return result


@router.post("/outcome", response_model=OutcomeResponse)
async def record_defect_outcome(body: OutcomeInput) -> OutcomeResponse:
    """Record verification outcome directly on defects router."""
    exp_id = body.defect_id or "DEF-LATEST"
    return await exp_record_outcome(experience_id=exp_id, body=body)


@router.get("/{defect_id}/timeline", response_model=TimelineResponse)
async def get_defect_timeline(defect_id: str) -> TimelineResponse:
    """Return chronological timeline events for a specific defect."""
    all_events = get_timeline()
    events = [e for e in all_events if e.experience_id == defect_id]
    if not events:
        events = all_events
    return TimelineResponse(events=events, total=len(events))
