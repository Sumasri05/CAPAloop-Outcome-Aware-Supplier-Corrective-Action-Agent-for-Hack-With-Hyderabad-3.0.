"""
CAPAloop — Recommendation service.

Builds structured corrective-action recommendations by orchestrating
Hindsight Recall → Evidence Analysis → Hindsight Reflect.

This module does NOT duplicate Hindsight's reflection capabilities.
It orchestrates the pipeline and packages the result.
"""

from __future__ import annotations

import inspect
import logging
import uuid

from ..hindsight import HindsightClient
from ..models import (
    AnalysisResponse,
    DefectInput,
    EvidenceGrade,
    Recommendation,
    SupportingCase,
    VerificationStep,
)
from .evidence import (
    build_limitations,
    build_recall_query,
    build_reflect_prompt,
    extract_cases_from_recall,
    find_contradictions,
    grade_evidence,
)

logger = logging.getLogger("capaloop.recommendations")


def analyze_defect(
    defect: DefectInput,
    client: HindsightClient,
) -> AnalysisResponse:
    """Full CAPA analysis pipeline for a new supplier defect.

    Steps:
      1. Build a focused recall query
      2. Call Hindsight Recall
      3. Extract structured cases from recalled memories
      4. Call Hindsight Reflect for synthesised reasoning
      5. Package the structured recommendation

    Args:
        defect: The new defect to analyze.
        client: Initialised HindsightClient.

    Returns:
        AnalysisResponse with recommendation, evidence, and limitations.
    """
    defect_id = f"DEF-{uuid.uuid4().hex[:8].upper()}"

    # Step 1: Build recall query
    recall_query = build_recall_query(
        supplier=defect.supplier,
        part_number=defect.part_number,
        defect_type=defect.defect_type,
        manufacturing_process=defect.manufacturing_process,
        root_cause_hypothesis=defect.root_cause_hypothesis,
    )
    logger.info("Analyzing defect %s — recalling from Hindsight", defect_id)

    # Step 2: Recall from Hindsight
    recall_result = client.recall(query=recall_query)
    recalled_texts = recall_result.results

    # Step 3: Extract structured cases
    cases = extract_cases_from_recall(recalled_texts)
    contradictions = find_contradictions(cases)
    evidence_grade = grade_evidence(cases)
    limitations = build_limitations(cases, contradictions)

    # Step 4: Reflect using Hindsight
    if recalled_texts:
        combined_evidence = "\n---\n".join(recalled_texts)
        reflect_prompt = build_reflect_prompt(
            defect_type=defect.defect_type,
            part_number=defect.part_number,
            supplier=defect.supplier,
            manufacturing_process=defect.manufacturing_process,
            recalled_text=combined_evidence,
        )
        reflect_result = client.reflect(query=reflect_prompt)
        reflection_text = reflect_result.text
    else:
        reflection_text = ""

    # Step 5: Build recommendation
    recommendation = _build_recommendation(
        cases=cases,
        contradictions=contradictions,
        evidence_grade=evidence_grade,
        limitations=limitations,
        reflection_text=reflection_text,
        defect=defect,
    )

    # Build verification plan
    verification_plan = _build_verification_plan(defect, evidence_grade)

    logger.info(
        "Analysis complete for %s — grade=%s, cases=%d",
        defect_id,
        evidence_grade.value,
        len(cases),
    )

    return AnalysisResponse(
        defect_id=defect_id,
        supplier=defect.supplier,
        part_number=defect.part_number,
        defect_type=defect.defect_type,
        historical_cases_found=len(cases),
        historical_cases=cases,
        recommendation=recommendation,
        verification_plan=verification_plan,
    )


async def aanalyze_defect(
    defect: DefectInput,
    client: HindsightClient,
) -> AnalysisResponse:
    """Async CAPA analysis pipeline for a new supplier defect."""
    defect_id = f"DEF-{uuid.uuid4().hex[:8].upper()}"

    recall_query = build_recall_query(
        supplier=defect.supplier,
        part_number=defect.part_number,
        defect_type=defect.defect_type,
        manufacturing_process=defect.manufacturing_process,
        root_cause_hypothesis=defect.root_cause_hypothesis,
    )
    logger.info("Analyzing defect %s — recalling from Hindsight (async)", defect_id)

    if hasattr(client, "arecall") and inspect.iscoroutinefunction(client.arecall):
        recall_result = await client.arecall(query=recall_query)
    else:
        recall_result = client.recall(query=recall_query)
    recalled_texts = recall_result.results

    cases = extract_cases_from_recall(recalled_texts)
    contradictions = find_contradictions(cases)
    evidence_grade = grade_evidence(cases)
    limitations = build_limitations(cases, contradictions)

    if recalled_texts:
        combined_evidence = "\n---\n".join(recalled_texts)
        reflect_prompt = build_reflect_prompt(
            defect_type=defect.defect_type,
            part_number=defect.part_number,
            supplier=defect.supplier,
            manufacturing_process=defect.manufacturing_process,
            recalled_text=combined_evidence,
        )
        if hasattr(client, "areflect") and inspect.iscoroutinefunction(client.areflect):
            reflect_result = await client.areflect(query=reflect_prompt)
        else:
            reflect_result = client.reflect(query=reflect_prompt)
        reflection_text = reflect_result.text
    else:
        reflection_text = ""

    recommendation = _build_recommendation(
        cases=cases,
        contradictions=contradictions,
        evidence_grade=evidence_grade,
        limitations=limitations,
        reflection_text=reflection_text,
        defect=defect,
    )
    verification_plan = _build_verification_plan(defect, evidence_grade)

    logger.info(
        "Async analysis complete for %s — grade=%s, cases=%d",
        defect_id,
        evidence_grade.value,
        len(cases),
    )

    return AnalysisResponse(
        defect_id=defect_id,
        supplier=defect.supplier,
        part_number=defect.part_number,
        defect_type=defect.defect_type,
        historical_cases_found=len(cases),
        historical_cases=cases,
        recommendation=recommendation,
        verification_plan=verification_plan,
    )


def _build_recommendation(
    cases: list[SupportingCase],
    contradictions: list[str],
    evidence_grade: EvidenceGrade,
    limitations: list[str],
    reflection_text: str,
    defect: DefectInput,
) -> Recommendation:
    """Build the structured recommendation from evidence and reflection."""

    if not cases:
        # No historical precedent
        return Recommendation(
            corrective_action=(
                "No strong historical precedent was found. "
                "Human quality-engineer review is required."
            ),
            reason=(
                "Hindsight recall returned no relevant historical "
                "supplier-quality experiences for this defect configuration. "
                "A quality engineer should investigate the root cause "
                "and design a corrective action without historical guidance."
            ),
            evidence_grade=EvidenceGrade.D,
            supporting_cases=[],
            contradictory_evidence=[],
            limitations=limitations,
        )

    # Extract corrective action from reflection text or cases
    if reflection_text:
        corrective_action = reflection_text
        reason = (
            "This recommendation is based on Hindsight's synthesis of "
            f"{len(cases)} historical supplier-quality experience(s). "
            "The corrective action was associated with the observed "
            "outcome(s) in similar historical contexts."
        )
    else:
        # Fallback: summarize from cases
        successful_cases = [c for c in cases if c.outcome == "successful"]
        if successful_cases:
            corrective_action = (
                f"Review historical case(s): "
                f"{', '.join(c.experience_id for c in successful_cases)}. "
                "These cases were associated with successful outcomes "
                "in similar contexts."
            )
        else:
            corrective_action = (
                "Historical cases exist but none show fully successful "
                "outcomes. Human quality-engineer review is strongly recommended."
            )
        reason = (
            f"Based on {len(cases)} recalled historical experience(s). "
            "Note: historical association does not establish causality."
        )

    return Recommendation(
        corrective_action=corrective_action,
        reason=reason,
        evidence_grade=evidence_grade,
        supporting_cases=cases,
        contradictory_evidence=contradictions,
        limitations=limitations,
    )


def _build_verification_plan(
    defect: DefectInput,
    evidence_grade: EvidenceGrade,
) -> list[VerificationStep]:
    """Build a verification plan appropriate to the evidence strength."""
    steps = [
        VerificationStep(
            step=1,
            action="Implement the corrective action and document changes.",
            duration="1-2 days",
            metric="Action completion confirmation",
        ),
        VerificationStep(
            step=2,
            action=(
                f"Conduct first-article inspection on {defect.part_number} "
                f"after corrective action."
            ),
            duration="1 day",
            metric="First-article pass/fail",
        ),
        VerificationStep(
            step=3,
            action=(
                f"Monitor {defect.defect_type} defect rate on "
                f"{defect.part_number} during production runs."
            ),
            duration="14 production days",
            metric="Defect rate (% defective)",
        ),
        VerificationStep(
            step=4,
            action="Compare defect rate before and after corrective action.",
            duration="After verification period",
            metric="Defect rate reduction percentage",
        ),
        VerificationStep(
            step=5,
            action="Check for recurrence during extended monitoring.",
            duration="30 additional days",
            metric="Recurrence count",
        ),
    ]

    # Add extra scrutiny for weak evidence
    if evidence_grade in (EvidenceGrade.C, EvidenceGrade.D):
        steps.append(VerificationStep(
            step=6,
            action=(
                "Evidence quality is low. Consider additional root-cause "
                "analysis (e.g., 5-Why, fishbone diagram) before relying "
                "solely on the recommended action."
            ),
            duration="2-3 days",
            metric="Root-cause analysis completion",
        ))

    return steps
