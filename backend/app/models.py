"""
CAPAloop — Domain models.

Pydantic models for supplier-quality defects, experiences,
corrective-action recommendations, and verification outcomes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


class Outcome(str, Enum):
    SUCCESSFUL = "successful"
    PARTIAL = "partial"
    FAILED = "failed"
    RECURRENCE = "recurrence"


class EvidenceGrade(str, Enum):
    """Evidence quality grading.

    A — Strong: verified outcome, no recurrence, adequate verification period.
    B — Moderate: verified outcome, minor caveats or limited verification.
    C — Weak: unverified or contradictory evidence.
    D — Insufficient: no relevant historical evidence available.
    """
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# ---------------------------------------------------------------------------
# Defect submission
# ---------------------------------------------------------------------------

class DefectInput(BaseModel):
    """A new supplier defect submitted for analysis."""
    supplier: str = Field(..., min_length=1)
    part_number: str = Field(..., min_length=1)
    defect_type: str = Field(..., min_length=1)
    severity: Severity
    manufacturing_process: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    root_cause_hypothesis: str = ""
    context: str = ""


# ---------------------------------------------------------------------------
# Historical experience
# ---------------------------------------------------------------------------

class Experience(BaseModel):
    """A complete supplier-quality experience with verification outcome."""
    experience_id: str = Field(default_factory=lambda: f"EXP-{uuid.uuid4().hex[:8].upper()}")
    supplier: str
    part_number: str
    defect_type: str
    severity: Severity
    manufacturing_process: str
    description: str
    root_cause_hypothesis: str = ""
    context: str = ""
    corrective_action: str = ""
    implementation_date: Optional[str] = None
    verification_period: str = ""
    follow_up_measurement: str = ""
    outcome: Optional[Outcome] = None
    recurrence: str = ""
    evidence_quality: Optional[EvidenceGrade] = None
    evidence_limitations: str = ""
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Recommendation (analysis output)
# ---------------------------------------------------------------------------

class SupportingCase(BaseModel):
    """A historical case supporting a recommendation."""
    experience_id: str
    summary: str
    outcome: str
    evidence_grade: str


class Recommendation(BaseModel):
    """Structured corrective-action recommendation."""
    corrective_action: str
    reason: str
    evidence_grade: EvidenceGrade
    supporting_cases: list[SupportingCase] = Field(default_factory=list)
    contradictory_evidence: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class VerificationStep(BaseModel):
    """A step in the suggested verification plan."""
    step: int
    action: str
    duration: str = ""
    metric: str = ""


class AnalysisResponse(BaseModel):
    """Full response for POST /api/defects/analyze."""
    defect_id: str
    supplier: str
    part_number: str
    defect_type: str
    historical_cases_found: int
    historical_cases: list[SupportingCase] = Field(default_factory=list)
    recommendation: Recommendation
    verification_plan: list[VerificationStep] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Outcome recording
# ---------------------------------------------------------------------------

class OutcomeInput(BaseModel):
    """Verification outcome submitted after corrective action."""
    corrective_action_taken: str = Field(..., min_length=1)
    verification_period: str = Field(..., min_length=1)
    measurement_before: str = Field(..., min_length=1)
    measurement_after: str = Field(..., min_length=1)
    outcome: Outcome
    recurrence: str = ""
    notes: str = ""
    evidence_quality: EvidenceGrade = EvidenceGrade.B
    defect_id: Optional[str] = None


class OutcomeResponse(BaseModel):
    """Response after recording a verification outcome."""
    experience_id: str
    status: str
    hindsight_retained: bool
    detail: str


# ---------------------------------------------------------------------------
# Learning timeline
# ---------------------------------------------------------------------------

class TimelineEvent(BaseModel):
    """A single event in the learning timeline."""
    timestamp: str
    event_type: str  # "defect_analyzed", "outcome_recorded", "experience_retained"
    experience_id: str
    summary: str


class TimelineResponse(BaseModel):
    """Response for GET /api/learning/timeline."""
    events: list[TimelineEvent]
    total: int
