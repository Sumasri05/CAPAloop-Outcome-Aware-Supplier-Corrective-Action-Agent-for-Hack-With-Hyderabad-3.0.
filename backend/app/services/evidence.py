"""
CAPAloop — Evidence analysis service.

Parses recalled Hindsight memories into structured historical cases,
grades evidence quality, and identifies contradictions.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from ..models import (
    EvidenceGrade,
    Outcome,
    SupportingCase,
)

logger = logging.getLogger("capaloop.evidence")


def build_recall_query(
    supplier: str,
    part_number: str,
    defect_type: str,
    manufacturing_process: str,
    root_cause_hypothesis: str = "",
) -> str:
    """Build a focused recall query from defect attributes.

    This query is sent to Hindsight Recall to find relevant
    historical supplier-quality experiences.
    """
    query_parts = [
        "Find historical supplier-quality experiences involving:",
        f"Supplier: {supplier}",
        f"Part: {part_number}",
        f"Defect: {defect_type}",
        f"Process: {manufacturing_process}",
    ]
    if root_cause_hypothesis:
        query_parts.append(f"Root-cause hypothesis: {root_cause_hypothesis}")

    query_parts.append(
        "\nPrioritize experiences containing corrective actions, "
        "verification measurements, outcomes (successful, partial, failed, "
        "recurrence), recurrence information, and evidence quality grades."
    )
    return "\n".join(query_parts)


def build_reflect_prompt(
    defect_type: str,
    part_number: str,
    supplier: str,
    manufacturing_process: str,
    recalled_text: str,
) -> str:
    """Build a reflection prompt for Hindsight Reflect.

    Instructs Hindsight to reason over the recalled evidence
    and produce a structured corrective-action recommendation.
    """
    return f"""\
Based on the historical supplier-quality experiences recalled below, \
analyze and respond to the following new defect situation:

NEW DEFECT:
- Defect type: {defect_type}
- Part: {part_number}
- Supplier: {supplier}
- Process: {manufacturing_process}

RECALLED HISTORICAL EVIDENCE:
{recalled_text}

Please provide:
1. What corrective action(s) were used in similar historical cases?
2. What were the measured outcomes (successful, partial, failed, recurrence)?
3. Was recurrence observed in any historical case?
4. What evidence quality supports each historical case?
5. Are there any contradictory cases (same defect, different outcome)?
6. What limitations should be considered?
7. What corrective action would you recommend for the new defect, and why?

CRITICAL INSTRUCTION:
Do NOT claim causality or that any corrective action CAUSED success. \
Use language such as: "The corrective action was associated with \
successful resolution in a similar historical context." \
Always note that correlation does not imply causation and association does not establish causality.
"""


def extract_cases_from_recall(
    recalled_results: list[str],
) -> list[SupportingCase]:
    """Parse recalled text into structured SupportingCase objects.

    This performs best-effort extraction of experience IDs, outcomes,
    and evidence grades from free-text recalled memories.
    """
    cases: list[SupportingCase] = []
    seen_ids: set[str] = set()

    for i, text in enumerate(recalled_results):
        exp_id = _extract_field(text, r"Experience ID:\s*(\S+)") or f"RECALLED-{i + 1:03d}"
        if exp_id in seen_ids:
            continue
        seen_ids.add(exp_id)

        outcome_str = _extract_field(text, r"Outcome:\s*(\w+)") or "unknown"
        grade_str = _extract_field(text, r"Evidence quality:\s*([A-D])") or "C"

        # Build a brief summary from the text (first 200 chars).
        summary = text[:200].replace("\n", " ").strip()
        if len(text) > 200:
            summary += "…"

        cases.append(SupportingCase(
            experience_id=exp_id,
            summary=summary,
            outcome=outcome_str.lower(),
            evidence_grade=grade_str,
        ))

    return cases


def grade_evidence(cases: list[SupportingCase]) -> EvidenceGrade:
    """Determine overall evidence grade from a set of historical cases.

    Grading logic:
    - A: ≥1 case with grade A and no contradictions.
    - B: ≥1 case with grade A or B, possible minor contradictions.
    - C: Only weak evidence or contradictory results.
    - D: No relevant cases found.
    """
    if not cases:
        return EvidenceGrade.D

    grades = [c.evidence_grade.upper() for c in cases]
    outcomes = [c.outcome.lower() for c in cases]

    has_a = "A" in grades
    has_b = "B" in grades
    has_contradiction = _has_contradictory_outcomes(outcomes)

    if has_a and not has_contradiction:
        return EvidenceGrade.A
    if (has_a or has_b) and not has_contradiction:
        return EvidenceGrade.B
    if has_a or has_b:
        return EvidenceGrade.B  # Strong evidence exists despite contradictions
    if cases:
        return EvidenceGrade.C
    return EvidenceGrade.D


def find_contradictions(cases: list[SupportingCase]) -> list[str]:
    """Identify contradictory evidence across historical cases.

    A contradiction exists when similar defects had different outcomes
    (e.g., one case successful, another failed).
    """
    contradictions: list[str] = []
    outcomes = {c.outcome.lower() for c in cases}

    positive = outcomes & {"successful"}
    negative = outcomes & {"failed", "recurrence"}

    if positive and negative:
        successful = [c for c in cases if c.outcome.lower() == "successful"]
        failed = [c for c in cases if c.outcome.lower() in ("failed", "recurrence")]
        contradictions.append(
            f"Contradictory evidence found: {len(successful)} case(s) show "
            f"successful outcomes, while {len(failed)} case(s) show "
            f"failed or recurring outcomes. Exercise caution."
        )

    if "partial" in outcomes and "successful" in outcomes:
        contradictions.append(
            "Some historical cases achieved only partial success, "
            "suggesting the corrective action may not fully resolve "
            "the defect in all contexts."
        )

    return contradictions


def build_limitations(
    cases: list[SupportingCase],
    contradictions: list[str],
) -> list[str]:
    """Build a list of evidence limitations."""
    limitations: list[str] = [
        "Historical association does not establish causality.",
    ]

    if not cases:
        limitations.append(
            "No historical precedent was found for this defect configuration."
        )
    elif len(cases) < 3:
        limitations.append(
            f"Only {len(cases)} historical case(s) found. "
            "Small sample size limits confidence."
        )

    if contradictions:
        limitations.append(
            "Contradictory evidence exists. "
            "The recommended action may not succeed in all contexts."
        )

    # Check if any case has weak evidence
    weak = [c for c in cases if c.evidence_grade.upper() in ("C", "D")]
    if weak:
        limitations.append(
            f"{len(weak)} case(s) have weak or unverified evidence (grade C/D)."
        )

    return limitations


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_field(text: str, pattern: str) -> Optional[str]:
    """Extract a single field value from free text using regex."""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _has_contradictory_outcomes(outcomes: list[str]) -> bool:
    """Check if outcomes contain both positive and negative results."""
    outcome_set = set(outcomes)
    positive = outcome_set & {"successful"}
    negative = outcome_set & {"failed", "recurrence"}
    return bool(positive and negative)
