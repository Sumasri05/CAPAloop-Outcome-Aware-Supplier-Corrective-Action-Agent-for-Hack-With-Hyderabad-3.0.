"""
CAPAloop — Experiences API.

POST /api/experiences/{experience_id}/outcome
"""

import asyncio
import inspect
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..hindsight import (
    HindsightAuthError,
    HindsightBankError,
    HindsightConnectionError,
    HindsightError,
)
from ..models import OutcomeInput, OutcomeResponse
from ..services.timeline import add_event

logger = logging.getLogger("capaloop.api.experiences")

router = APIRouter(prefix="/api/experiences", tags=["experiences"])

# In-memory store for experiences awaiting outcome — Phase 2 only.
_pending_experiences: dict[str, dict] = {}


def register_pending_experience(
    experience_id: str,
    defect_data: dict,
) -> None:
    """Register a defect analysis result as pending outcome verification."""
    _pending_experiences[experience_id] = {
        **defect_data,
        "experience_id": experience_id,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }


def _get_hindsight_client():
    """Import and retrieve the Hindsight client from main app state."""
    from ..main import _get_client
    return _get_client()


@router.post(
    "/{experience_id}/outcome",
    response_model=OutcomeResponse,
)
async def record_outcome(
    experience_id: str,
    body: OutcomeInput,
) -> OutcomeResponse:
    """Record the verification outcome for a corrective action.

    After recording, the complete verified experience is retained
    in Hindsight so it becomes available for future recalls.
    """
    client = _get_hindsight_client()

    # Build the full experience text for Hindsight retention.
    # Include both the defect context (if available) and the outcome.
    pending = _pending_experiences.get(experience_id, {})

    experience_text = _format_experience_for_retention(
        experience_id=experience_id,
        pending=pending,
        outcome_data=body,
    )

    # Retain in Hindsight
    try:
        if hasattr(client, "aretain") and inspect.iscoroutinefunction(client.aretain):
            retain_result = await client.aretain(content=experience_text)
        else:
            retain_result = client.retain(content=experience_text)
        hindsight_retained = retain_result.success
    except HindsightAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HindsightBankError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HindsightConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HindsightError as exc:
        logger.error("Failed to retain experience %s: %s", experience_id, exc)
        hindsight_retained = False

    # Record timeline events
    add_event(
        event_type="outcome_recorded",
        experience_id=experience_id,
        summary=(
            f"Outcome recorded: {body.outcome.value}. "
            f"Measurement: {body.measurement_before} → {body.measurement_after}. "
            f"Evidence quality: {body.evidence_quality.value}."
        ),
    )

    if hindsight_retained:
        add_event(
            event_type="experience_retained",
            experience_id=experience_id,
            summary=(
                f"Verified experience retained in Hindsight. "
                f"Outcome: {body.outcome.value}. "
                f"Now available for future recall."
            ),
        )

    # Clean up pending
    _pending_experiences.pop(experience_id, None)

    return OutcomeResponse(
        experience_id=experience_id,
        status="success" if hindsight_retained else "partial",
        hindsight_retained=hindsight_retained,
        detail=(
            "Experience retained in Hindsight and available for future recall."
            if hindsight_retained
            else "Outcome recorded but Hindsight retention failed. "
            "The experience may not be available for future recall."
        ),
    )


def _format_experience_for_retention(
    experience_id: str,
    pending: dict,
    outcome_data: OutcomeInput,
) -> str:
    """Format a verified experience as structured text for Hindsight."""
    lines = [
        f"[VERIFIED SUPPLIER-QUALITY EXPERIENCE]",
        f"",
        f"Experience ID: {experience_id}",
    ]

    if pending:
        lines.extend([
            f"Supplier: {pending.get('supplier', 'Unknown')}",
            f"Part: {pending.get('part_number', 'Unknown')}",
            f"Defect: {pending.get('defect_type', 'Unknown')}",
            f"Severity: {pending.get('severity', 'Unknown')}",
            f"Manufacturing Process: {pending.get('manufacturing_process', 'Unknown')}",
            f"Description: {pending.get('description', '')}",
            f"Root-cause hypothesis: {pending.get('root_cause_hypothesis', '')}",
            f"Context: {pending.get('context', '')}",
        ])

    lines.extend([
        f"",
        f"Corrective action: {outcome_data.corrective_action_taken}",
        f"Verification period: {outcome_data.verification_period}",
        f"",
        f"Follow-up measurement:",
        f"  Before: {outcome_data.measurement_before}",
        f"  After: {outcome_data.measurement_after}",
        f"",
        f"Outcome: {outcome_data.outcome.value.capitalize()}",
        f"Recurrence: {outcome_data.recurrence or 'Not reported'}",
        f"",
        f"Evidence quality: {outcome_data.evidence_quality.value}",
        f"Evidence limitation: The intervention was associated with the "
        f"observed outcome in this historical context; causality has not "
        f"been established.",
        f"",
        f"Notes: {outcome_data.notes or 'None'}",
        f"",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
    ])

    return "\n".join(lines)
