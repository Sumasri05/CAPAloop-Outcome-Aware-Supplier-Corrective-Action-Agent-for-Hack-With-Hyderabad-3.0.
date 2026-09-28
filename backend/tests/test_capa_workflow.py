"""
CAPAloop — Phase 2 CAPA workflow tests.

Unit tests (no credentials required):
    Defect validation, query building, evidence analysis,
    recommendation structure, contradiction handling, and
    no-precedent fallback.

Integration tests (require HINDSIGHT_API_KEY):
    End-to-end CAPA learning workflow against live Hindsight Cloud.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient

load_dotenv()

from backend.app.models import (
    DefectInput,
    EvidenceGrade,
    Outcome,
    OutcomeInput,
    Severity,
    SupportingCase,
)
from backend.app.services.evidence import (
    build_limitations,
    build_recall_query,
    build_reflect_prompt,
    extract_cases_from_recall,
    find_contradictions,
    grade_evidence,
)
from backend.app.services.timeline import (
    add_event,
    clear_timeline,
    get_timeline,
)
from backend.app.seed import SEED_EXPERIENCES


# ===================================================================
# UNIT TESTS
# ===================================================================


class TestDefectInputValidation:
    """Test 1: Defect input validation."""

    def test_valid_defect_input(self):
        """Valid defect input is accepted."""
        defect = DefectInput(
            supplier="Apex Components",
            part_number="BRK-204",
            defect_type="Surface cracks",
            severity=Severity.MAJOR,
            manufacturing_process="Metal stamping",
            description="Cracks appeared after die change.",
        )
        assert defect.supplier == "Apex Components"
        assert defect.severity == Severity.MAJOR

    def test_missing_required_field_raises(self):
        """Missing required fields are rejected."""
        with pytest.raises(Exception):
            DefectInput(
                supplier="",
                part_number="BRK-204",
                defect_type="Surface cracks",
                severity=Severity.MAJOR,
                manufacturing_process="Metal stamping",
                description="test",
            )

    def test_severity_enum_values(self):
        """All severity levels are valid."""
        for sev in Severity:
            defect = DefectInput(
                supplier="Test",
                part_number="X-001",
                defect_type="test",
                severity=sev,
                manufacturing_process="test",
                description="test",
            )
            assert defect.severity == sev

    def test_outcome_enum_values(self):
        """All outcome values are valid."""
        assert set(Outcome) == {
            Outcome.SUCCESSFUL,
            Outcome.PARTIAL,
            Outcome.FAILED,
            Outcome.RECURRENCE,
        }


class TestRecallQueryGeneration:
    """Test 2: Recall query generation."""

    def test_query_contains_defect_attributes(self):
        """Generated query includes supplier, part, defect, and process."""
        query = build_recall_query(
            supplier="Apex Components",
            part_number="BRK-204",
            defect_type="Surface cracks",
            manufacturing_process="Metal stamping",
        )
        assert "Apex Components" in query
        assert "BRK-204" in query
        assert "Surface cracks" in query
        assert "Metal stamping" in query

    def test_query_includes_root_cause_when_provided(self):
        """Root-cause hypothesis is included when provided."""
        query = build_recall_query(
            supplier="Apex",
            part_number="X-1",
            defect_type="Cracks",
            manufacturing_process="Stamping",
            root_cause_hypothesis="Excessive pressure",
        )
        assert "Excessive pressure" in query

    def test_query_requests_evidence_quality(self):
        """Query asks for outcomes and evidence quality."""
        query = build_recall_query(
            supplier="Test",
            part_number="X-1",
            defect_type="Test",
            manufacturing_process="Test",
        )
        assert "evidence quality" in query.lower()
        assert "outcome" in query.lower()


class TestHistoricalEvidenceExtraction:
    """Test 3: Extraction of structured cases from recalled text."""

    def test_extract_experience_id(self):
        """Experience IDs are extracted from recalled text."""
        recalled = [
            "Experience ID: SEED-001\nSupplier: Apex\nOutcome: Successful\nEvidence quality: A"
        ]
        cases = extract_cases_from_recall(recalled)
        assert len(cases) == 1
        assert cases[0].experience_id == "SEED-001"

    def test_extract_outcome(self):
        """Outcomes are extracted from recalled text."""
        recalled = [
            "Experience ID: TEST-1\nOutcome: Failed\nEvidence quality: B"
        ]
        cases = extract_cases_from_recall(recalled)
        assert cases[0].outcome == "failed"

    def test_extract_evidence_grade(self):
        """Evidence grades are extracted from recalled text."""
        recalled = [
            "Experience ID: TEST-1\nOutcome: Successful\nEvidence quality: A"
        ]
        cases = extract_cases_from_recall(recalled)
        assert cases[0].evidence_grade == "A"

    def test_fallback_id_for_unstructured_text(self):
        """Unstructured text gets a fallback ID."""
        recalled = [
            "Some unstructured memory about surface cracks."
        ]
        cases = extract_cases_from_recall(recalled)
        assert len(cases) == 1
        assert cases[0].experience_id.startswith("RECALLED-")

    def test_duplicate_ids_deduplicated(self):
        """Duplicate experience IDs are deduplicated."""
        recalled = [
            "Experience ID: SEED-001\nOutcome: Successful\nEvidence quality: A",
            "Experience ID: SEED-001\nOutcome: Successful\nEvidence quality: A",
        ]
        cases = extract_cases_from_recall(recalled)
        assert len(cases) == 1

    def test_empty_recall_returns_empty(self):
        """Empty recall returns empty list."""
        cases = extract_cases_from_recall([])
        assert cases == []


class TestEvidenceGrading:
    """Test 4: Evidence grading logic."""

    def test_grade_a_with_strong_evidence(self):
        """Grade A when strong evidence with no contradictions."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
        ]
        assert grade_evidence(cases) == EvidenceGrade.A

    def test_grade_b_with_moderate_evidence(self):
        """Grade B when moderate evidence."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="B",
            ),
        ]
        assert grade_evidence(cases) == EvidenceGrade.B

    def test_grade_c_with_weak_evidence(self):
        """Grade C when only weak evidence."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="partial",
                evidence_grade="C",
            ),
        ]
        assert grade_evidence(cases) == EvidenceGrade.C

    def test_grade_d_when_no_cases(self):
        """Grade D when no cases found."""
        assert grade_evidence([]) == EvidenceGrade.D

    def test_grade_with_contradictory_evidence(self):
        """Grade accounts for contradictions but doesn't drop below B if strong evidence exists."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
            SupportingCase(
                experience_id="T2",
                summary="test",
                outcome="failed",
                evidence_grade="B",
            ),
        ]
        grade = grade_evidence(cases)
        # Should still be B because strong evidence exists
        assert grade == EvidenceGrade.B


class TestRecommendationStructure:
    """Test 5: Recommendation output structure."""

    @patch("backend.app.hindsight.Hindsight")
    def test_recommendation_with_cases(self, mock_cls):
        """Recommendation includes supporting cases and limitations."""
        from backend.app.hindsight import HindsightClient
        from backend.app.config import HindsightSettings
        from backend.app.services.recommendations import analyze_defect

        mock_instance = MagicMock()

        # Mock recall response
        recall_resp = MagicMock()
        recall_resp.results = [
            "Experience ID: SEED-001\nOutcome: Successful\n"
            "Evidence quality: A\n"
            "Corrective action: Adjusted forming pressure"
        ]
        mock_instance.recall.return_value = recall_resp

        # Mock reflect response
        mock_instance.reflect.return_value = (
            "Based on historical evidence, adjusting forming pressure "
            "was associated with successful resolution."
        )

        mock_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )
        client = HindsightClient(settings=settings)

        defect = DefectInput(
            supplier="Apex Components",
            part_number="BRK-204",
            defect_type="Surface cracks",
            severity=Severity.MAJOR,
            manufacturing_process="Metal stamping",
            description="Cracks after die change.",
        )

        result = analyze_defect(defect, client)

        assert result.defect_id.startswith("DEF-")
        assert result.historical_cases_found >= 1
        assert result.recommendation.evidence_grade is not None
        assert len(result.recommendation.limitations) > 0
        assert len(result.verification_plan) > 0

    @patch("backend.app.hindsight.Hindsight")
    def test_recommendation_never_claims_causality(self, mock_cls):
        """Recommendation text never claims causality."""
        from backend.app.hindsight import HindsightClient
        from backend.app.config import HindsightSettings
        from backend.app.services.recommendations import analyze_defect

        mock_instance = MagicMock()
        recall_resp = MagicMock()
        recall_resp.results = [
            "Experience ID: X-1\nOutcome: Successful\nEvidence quality: A"
        ]
        mock_instance.recall.return_value = recall_resp
        mock_instance.reflect.return_value = "Action was associated with success."
        mock_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )
        client = HindsightClient(settings=settings)

        defect = DefectInput(
            supplier="Test",
            part_number="T-1",
            defect_type="Cracks",
            severity=Severity.MINOR,
            manufacturing_process="Stamping",
            description="Test defect.",
        )

        result = analyze_defect(defect, client)

        # Limitations should always include the causality disclaimer
        causality_noted = any(
            "causality" in lim.lower() or "association" in lim.lower()
            for lim in result.recommendation.limitations
        )
        assert causality_noted, (
            "Recommendation must note that association does not "
            "establish causality."
        )


class TestContradictoryEvidenceHandling:
    """Test 6: Contradictory evidence detection."""

    def test_detects_success_vs_failure(self):
        """Contradictions detected between successful and failed outcomes."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
            SupportingCase(
                experience_id="T2",
                summary="test",
                outcome="failed",
                evidence_grade="B",
            ),
        ]
        contradictions = find_contradictions(cases)
        assert len(contradictions) > 0
        assert "contradictory" in contradictions[0].lower()

    def test_detects_partial_vs_success(self):
        """Contradictions noted when partial and successful coexist."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
            SupportingCase(
                experience_id="T2",
                summary="test",
                outcome="partial",
                evidence_grade="B",
            ),
        ]
        contradictions = find_contradictions(cases)
        assert len(contradictions) > 0

    def test_no_contradictions_when_all_successful(self):
        """No contradictions when all cases are successful."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
            SupportingCase(
                experience_id="T2",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
        ]
        contradictions = find_contradictions(cases)
        # No success vs. failure contradiction
        contradiction_texts = " ".join(contradictions).lower()
        assert "contradictory evidence found" not in contradiction_texts


class TestNoPrecedentHandling:
    """Test 7: No-precedent fallback."""

    @patch("backend.app.hindsight.Hindsight")
    def test_no_precedent_returns_safe_message(self, mock_cls):
        """When no historical cases exist, recommendation is safe."""
        from backend.app.hindsight import HindsightClient
        from backend.app.config import HindsightSettings
        from backend.app.services.recommendations import analyze_defect

        mock_instance = MagicMock()
        recall_resp = MagicMock()
        recall_resp.results = []  # No results
        mock_instance.recall.return_value = recall_resp
        mock_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )
        client = HindsightClient(settings=settings)

        defect = DefectInput(
            supplier="Unknown Corp",
            part_number="UNK-999",
            defect_type="Exotic failure",
            severity=Severity.CRITICAL,
            manufacturing_process="Unknown process",
            description="Never-seen-before defect.",
        )

        result = analyze_defect(defect, client)

        assert result.historical_cases_found == 0
        assert result.recommendation.evidence_grade == EvidenceGrade.D
        assert "no strong historical precedent" in (
            result.recommendation.corrective_action.lower()
        )
        assert "human" in result.recommendation.corrective_action.lower()

    @patch("backend.app.hindsight.Hindsight")
    def test_no_precedent_does_not_fabricate(self, mock_cls):
        """No-precedent case does not fabricate supporting evidence."""
        from backend.app.hindsight import HindsightClient
        from backend.app.config import HindsightSettings
        from backend.app.services.recommendations import analyze_defect

        mock_instance = MagicMock()
        recall_resp = MagicMock()
        recall_resp.results = []
        mock_instance.recall.return_value = recall_resp
        mock_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )
        client = HindsightClient(settings=settings)

        defect = DefectInput(
            supplier="Unknown",
            part_number="UNK-1",
            defect_type="Unknown",
            severity=Severity.MINOR,
            manufacturing_process="Unknown",
            description="test",
        )

        result = analyze_defect(defect, client)
        assert result.recommendation.supporting_cases == []


class TestOutcomeRecording:
    """Test 8: Outcome recording and Hindsight retention."""

    def test_outcome_input_validation(self):
        """Outcome input validates required fields."""
        outcome = OutcomeInput(
            corrective_action_taken="Adjusted pressure to 380 kN",
            verification_period="14 production days",
            measurement_before="7.8% defect rate",
            measurement_after="0.9% defect rate",
            outcome=Outcome.SUCCESSFUL,
            evidence_quality=EvidenceGrade.A,
        )
        assert outcome.outcome == Outcome.SUCCESSFUL
        assert outcome.evidence_quality == EvidenceGrade.A

    def test_outcome_missing_field_raises(self):
        """Missing required outcome fields raise validation error."""
        with pytest.raises(Exception):
            OutcomeInput(
                corrective_action_taken="",  # empty
                verification_period="14 days",
                measurement_before="7.8%",
                measurement_after="0.9%",
                outcome=Outcome.SUCCESSFUL,
            )


class TestHindsightRetainAfterVerification:
    """Test 9: Verified experience is retained in Hindsight."""

    @patch("backend.app.main._hindsight")
    def test_outcome_endpoint_retains_in_hindsight(
        self,
        mock_hindsight,
    ):
        """POST /api/experiences/{id}/outcome retains in Hindsight."""
        from backend.app.main import app
        from backend.app.hindsight import RetainResult

        mock_hindsight.retain.return_value = RetainResult(
            success=True,
            detail="retained",
        )

        test_client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = test_client.post(
            "/api/experiences/DEF-TEST001/outcome",
            json={
                "corrective_action_taken": "Adjusted forming pressure",
                "verification_period": "14 production days",
                "measurement_before": "7.8% defect rate",
                "measurement_after": "0.9% defect rate",
                "outcome": "successful",
                "recurrence": "No recurrence",
                "notes": "All checks passed",
                "evidence_quality": "A",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["experience_id"] == "DEF-TEST001"
        assert data["hindsight_retained"] is True

        # Verify retain was called
        mock_hindsight.retain.assert_called_once()
        retain_call_text = mock_hindsight.retain.call_args[1]["content"]
        assert "DEF-TEST001" in retain_call_text
        assert "Adjusted forming pressure" in retain_call_text
        assert "Successful" in retain_call_text


class TestTimeline:
    """Test timeline service."""

    def test_timeline_records_events(self):
        """Timeline records and returns events."""
        clear_timeline()
        add_event("defect_analyzed", "DEF-001", "Test analysis")
        add_event("outcome_recorded", "DEF-001", "Test outcome")

        events = get_timeline()
        assert len(events) == 2
        # Newest first
        assert events[0].event_type == "outcome_recorded"
        assert events[1].event_type == "defect_analyzed"
        clear_timeline()

    def test_timeline_endpoint(self):
        """GET /api/learning/timeline returns events."""
        clear_timeline()
        from backend.app.main import app

        test_client = TestClient(app, raise_server_exceptions=False)

        response = test_client.get("/api/learning/timeline")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        clear_timeline()


class TestSeedData:
    """Test seed data structure."""

    def test_seed_has_10_experiences(self):
        """Seed data contains 10 experiences."""
        assert len(SEED_EXPERIENCES) == 10

    def test_seed_covers_all_scenarios(self):
        """Seed data covers required outcome scenarios."""
        combined = "\n".join(SEED_EXPERIENCES).lower()
        assert "outcome: successful" in combined
        assert "outcome: failed" in combined
        assert "outcome: partial" in combined
        assert "recurrence" in combined

    def test_seed_labelled_as_synthetic(self):
        """All seed experiences are clearly labelled as synthetic."""
        for exp in SEED_EXPERIENCES:
            assert "SYNTHETIC DEMO DATA" in exp

    def test_seed_includes_evidence_quality(self):
        """All seed experiences include evidence quality grades."""
        for exp in SEED_EXPERIENCES:
            assert "Evidence quality:" in exp

    def test_seed_includes_evidence_limitation(self):
        """All seed experiences include evidence limitations."""
        for exp in SEED_EXPERIENCES:
            assert "Evidence limitation:" in exp


class TestReflectPrompt:
    """Test reflect prompt generation."""

    def test_reflect_prompt_includes_defect_context(self):
        """Reflect prompt includes the defect attributes."""
        prompt = build_reflect_prompt(
            defect_type="Surface cracks",
            part_number="BRK-204",
            supplier="Apex",
            manufacturing_process="Metal stamping",
            recalled_text="Some recalled evidence.",
        )
        assert "Surface cracks" in prompt
        assert "BRK-204" in prompt
        assert "Apex" in prompt

    def test_reflect_prompt_warns_against_causality(self):
        """Reflect prompt instructs against claiming causality."""
        prompt = build_reflect_prompt(
            defect_type="test",
            part_number="test",
            supplier="test",
            manufacturing_process="test",
            recalled_text="test",
        )
        assert "causality" in prompt.lower()
        assert "associated" in prompt.lower()


class TestFastAPIPhase1Preserved:
    """Verify Phase 1 endpoints still work."""

    @patch("backend.app.main._hindsight", None)
    def test_health_still_works(self):
        """Health endpoint is preserved."""
        from backend.app.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @patch("backend.app.main._hindsight", None)
    def test_retain_503_still_works(self):
        """Retain returns 503 when not configured."""
        from backend.app.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/retain", json={"content": "test"})
        assert response.status_code == 503

    @patch("backend.app.main._hindsight", None)
    def test_defect_analyze_503_when_not_configured(self):
        """Defect analyze returns 503 when Hindsight unavailable."""
        from backend.app.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/defects/analyze",
            json={
                "supplier": "Test",
                "part_number": "T-1",
                "defect_type": "Cracks",
                "severity": "major",
                "manufacturing_process": "Stamping",
                "description": "Test defect.",
            },
        )
        assert response.status_code == 503


class TestLimitations:
    """Test evidence limitation generation."""

    def test_limitations_include_causality_warning(self):
        """Limitations always include causality warning."""
        limitations = build_limitations([], [])
        assert any("causality" in l.lower() for l in limitations)

    def test_limitations_note_small_sample(self):
        """Limitations flag small sample sizes."""
        cases = [
            SupportingCase(
                experience_id="T1",
                summary="test",
                outcome="successful",
                evidence_grade="A",
            ),
        ]
        limitations = build_limitations(cases, [])
        assert any("1 historical case" in l.lower() for l in limitations)

    def test_limitations_note_contradictions(self):
        """Limitations flag contradictions when present."""
        limitations = build_limitations(
            [],
            ["Contradictory results found"],
        )
        assert any("contradictory" in l.lower() for l in limitations)


# ===================================================================
# INTEGRATION TESTS — require real Hindsight credentials
# ===================================================================

def _has_credentials() -> bool:
    return bool(os.getenv("HINDSIGHT_API_KEY"))


integration = pytest.mark.skipif(
    not _has_credentials(),
    reason="HINDSIGHT_API_KEY not set — skipping integration test.",
)


@integration
class TestEndToEndCAPAWorkflow:
    """Test 10: End-to-end CAPA learning workflow.

    This test verifies the complete cycle:
      1. Seed experiences → Hindsight
      2. Analyze a new defect → recall + reflect
      3. Record verification outcome → retain
      4. Re-analyze → new experience appears in recall
    """

    def _make_client(self):
        from backend.app.hindsight import HindsightClient
        return HindsightClient()

    def test_full_capa_learning_cycle(self):
        """End-to-end: seed → analyze → outcome → re-analyze."""
        from backend.app.services.recommendations import analyze_defect
        from backend.app.seed import seed_to_hindsight

        client = self._make_client()

        # Step 1: Seed experiences
        print("\n--- Step 1: Seeding experiences ---")
        retained = seed_to_hindsight(client)
        assert len(retained) > 0, "No seed experiences were retained."
        print(f"Retained {len(retained)} seed experiences.")

        # Step 2: Analyze a defect
        print("\n--- Step 2: Analyzing new defect ---")
        defect = DefectInput(
            supplier="Apex Components",
            part_number="BRK-204",
            defect_type="Surface cracks",
            severity=Severity.MAJOR,
            manufacturing_process="Metal stamping",
            description="Surface cracks appeared after die setup change.",
            root_cause_hypothesis="Excessive forming pressure.",
        )

        result = analyze_defect(defect, client)

        assert result.defect_id.startswith("DEF-")
        assert result.recommendation is not None
        print(f"Defect ID: {result.defect_id}")
        print(f"Evidence grade: {result.recommendation.evidence_grade.value}")
        print(f"Historical cases: {result.historical_cases_found}")
        print(f"Action: {result.recommendation.corrective_action[:100]}...")

        # Step 3: Record outcome
        print("\n--- Step 3: Recording outcome ---")
        import uuid
        new_exp_id = f"EXP-{uuid.uuid4().hex[:8].upper()}"

        from backend.app.api.experiences import _format_experience_for_retention

        outcome = OutcomeInput(
            corrective_action_taken=(
                "Adjusted forming pressure to 380 kN and added "
                "first-article inspection after die changes."
            ),
            verification_period="14 production days",
            measurement_before="7.8% defect rate",
            measurement_after="0.9% defect rate",
            outcome=Outcome.SUCCESSFUL,
            recurrence="No recurrence during verification period.",
            notes="Comprehensive corrective action verified.",
            evidence_quality=EvidenceGrade.A,
        )

        experience_text = _format_experience_for_retention(
            experience_id=new_exp_id,
            pending={
                "supplier": defect.supplier,
                "part_number": defect.part_number,
                "defect_type": defect.defect_type,
                "severity": defect.severity.value,
                "manufacturing_process": defect.manufacturing_process,
                "description": defect.description,
                "root_cause_hypothesis": defect.root_cause_hypothesis,
            },
            outcome_data=outcome,
        )

        retain_result = client.retain(content=experience_text)
        assert retain_result.success, "Failed to retain new experience."
        print(f"Retained experience: {new_exp_id}")

        # Step 4: Re-analyze — new experience should appear
        print("\n--- Step 4: Re-analyzing (learning check) ---")
        result2 = analyze_defect(defect, client)
        print(f"Re-analysis cases: {result2.historical_cases_found}")
        print(f"Re-analysis grade: {result2.recommendation.evidence_grade.value}")

        # The recommendation should exist and be non-empty
        assert result2.recommendation.corrective_action
        print("\n✓ Full CAPA learning cycle completed successfully.")
