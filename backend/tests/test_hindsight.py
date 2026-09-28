"""
CAPAloop — Phase 1 Tests.

Unit tests (no credentials required):
    Configuration, client initialization, error handling, and FastAPI endpoints.

Integration tests (require HINDSIGHT_API_KEY):
    Live Retain → Recall → Reflect tests against Hindsight Cloud.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient

# Load .env BEFORE pytest evaluates the integration-test skip condition.
load_dotenv()

# ---------------------------------------------------------------------------
# Synthetic test experience (CASE-001) — clearly labelled as demo data
# ---------------------------------------------------------------------------

SYNTHETIC_EXPERIENCE = """\
[SYNTHETIC DEMO DATA — CAPAloop Phase 1]

Experience ID: CASE-001
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Surface cracks appeared after a die setup change.

Root-cause hypothesis:
Excessive forming pressure or die alignment drift.

Corrective action:
Adjusted forming pressure and added first-article inspection after die changes.

Verification period: 14 production days.

Follow-up measurement:
Defect rate reduced from 7.8% to 0.9%.

Outcome: Successful.

Recurrence: No recurrence during the verification period.

Evidence quality: A.

Evidence limitation:
The intervention was associated with successful resolution \
in this historical context; causality has not been established.
"""

RECALL_QUERY = """\
Find historical supplier-quality experiences involving:

Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Process: Metal stamping

Prioritize experiences containing corrective actions, \
verification measurements, outcomes, recurrence information, \
and evidence quality.
"""

REFLECT_QUERY = """\
Based on the historical supplier-quality experience:

1. What corrective action was used?
2. What was the measured outcome?
3. Was recurrence observed?
4. What evidence supports the action?
5. What limitations should be considered?
6. What should a quality engineer consider if a similar defect occurs?

IMPORTANT: Do NOT claim causality. Use language such as \
"The corrective action was associated with successful resolution \
in a similar historical context."
"""


# ===================================================================
# UNIT TESTS — no real Hindsight credentials needed
# ===================================================================

class TestConfiguration:
    """Test configuration loading and missing-config handling."""

    def test_load_settings_from_env(self):
        """Configuration loads correctly from environment."""
        with patch.dict(
            os.environ,
            {
                "HINDSIGHT_API_URL": "https://test.example.com",
                "HINDSIGHT_API_KEY": "test-key-abc123",
                "HINDSIGHT_BANK_ID": "test-bank",
            },
        ):
            from backend.app.config import load_settings

            settings = load_settings()

            assert settings.api_url == "https://test.example.com"
            assert settings.api_key == "test-key-abc123"
            assert settings.bank_id == "test-bank"

    def test_missing_configuration_raises_error(self):
        """Missing configuration is handled safely."""
        with patch.dict(
            os.environ,
            {
                "HINDSIGHT_API_URL": "",
                "HINDSIGHT_API_KEY": "",
                "HINDSIGHT_BANK_ID": "",
            },
            clear=False,
        ):
            from backend.app.config import (
                ConfigurationError,
                load_settings,
            )

            with pytest.raises(
                ConfigurationError,
                match="Missing or empty",
            ):
                load_settings()


class TestHindsightClientInit:
    """Test Hindsight client initialization."""

    @patch("backend.app.hindsight.Hindsight")
    def test_client_initialises(self, mock_hindsight_cls):
        """Hindsight client initializes correctly."""
        from backend.app.config import HindsightSettings
        from backend.app.hindsight import HindsightClient

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )

        client = HindsightClient(settings=settings)

        mock_hindsight_cls.assert_called_once_with(
            base_url="https://test.example.com",
            api_key="test-key",
        )

        assert client._bank_id == "test-bank"


class TestErrorHandling:
    """Test failure handling without a live Hindsight instance."""

    @patch("backend.app.hindsight.Hindsight")
    def test_retain_failure_does_not_claim_success(
        self,
        mock_hindsight_cls,
    ):
        """Hindsight failure is handled safely — retain."""
        from backend.app.config import HindsightSettings
        from backend.app.hindsight import (
            HindsightClient,
            HindsightRetainError,
        )

        mock_instance = MagicMock()
        mock_instance.retain.side_effect = RuntimeError(
            "500 Internal Server Error"
        )
        mock_hindsight_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )

        client = HindsightClient(settings=settings)

        with pytest.raises(HindsightRetainError):
            client.retain(content="test content")

    @patch("backend.app.hindsight.Hindsight")
    def test_no_result_recall_returns_empty(
        self,
        mock_hindsight_cls,
    ):
        """No-result recall does not fabricate evidence."""
        from backend.app.config import HindsightSettings
        from backend.app.hindsight import HindsightClient

        mock_instance = MagicMock()

        mock_response = MagicMock()
        mock_response.results = []

        mock_instance.recall.return_value = mock_response
        mock_hindsight_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )

        client = HindsightClient(settings=settings)

        result = client.recall(
            query="nonexistent part XYZ-999"
        )

        assert result.results == []

    @patch("backend.app.hindsight.Hindsight")
    def test_auth_error_is_classified(
        self,
        mock_hindsight_cls,
    ):
        """401 errors are classified as authentication errors."""
        from backend.app.config import HindsightSettings
        from backend.app.hindsight import (
            HindsightAuthError,
            HindsightClient,
        )

        mock_instance = MagicMock()
        mock_instance.retain.side_effect = RuntimeError(
            "401 Unauthorized"
        )
        mock_hindsight_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="bad-key",
            bank_id="test-bank",
        )

        client = HindsightClient(settings=settings)

        with pytest.raises(
            HindsightAuthError,
            match="authentication failed",
        ):
            client.retain(content="test")

    @patch("backend.app.hindsight.Hindsight")
    def test_reflect_failure_does_not_fabricate(
        self,
        mock_hindsight_cls,
    ):
        """Reflect failure does not fabricate a recommendation."""
        from backend.app.config import HindsightSettings
        from backend.app.hindsight import (
            HindsightClient,
            HindsightReflectError,
        )

        mock_instance = MagicMock()
        mock_instance.reflect.side_effect = RuntimeError(
            "timeout"
        )
        mock_hindsight_cls.return_value = mock_instance

        settings = HindsightSettings(
            api_url="https://test.example.com",
            api_key="test-key",
            bank_id="test-bank",
        )

        client = HindsightClient(settings=settings)

        with pytest.raises(
            (HindsightReflectError, Exception)
        ):
            client.reflect(query="test")


class TestFastAPIEndpoints:
    """Test the HTTP layer with a mocked Hindsight backend."""

    @patch("backend.app.main._hindsight", None)
    def test_health_without_hindsight(self):
        """Health returns ok when Hindsight is not configured."""
        from backend.app.main import app

        client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["hindsight"] == "not_configured"

    @patch("backend.app.main._hindsight", None)
    def test_retain_503_when_not_configured(self):
        """Retain returns 503 when Hindsight is unavailable."""
        from backend.app.main import app

        client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = client.post(
            "/retain",
            json={"content": "test"},
        )

        assert response.status_code == 503

    @patch("backend.app.main._hindsight", None)
    def test_recall_503_when_not_configured(self):
        """Recall returns 503 when Hindsight is unavailable."""
        from backend.app.main import app

        client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = client.post(
            "/recall",
            json={"query": "test"},
        )

        assert response.status_code == 503

    @patch("backend.app.main._hindsight", None)
    def test_reflect_503_when_not_configured(self):
        """Reflect returns 503 when Hindsight is unavailable."""
        from backend.app.main import app

        client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = client.post(
            "/reflect",
            json={"query": "test"},
        )

        assert response.status_code == 503


# ===================================================================
# INTEGRATION TESTS — require real Hindsight credentials
# ===================================================================

def _has_hindsight_credentials() -> bool:
    """Check whether Hindsight credentials are available."""
    return bool(os.getenv("HINDSIGHT_API_KEY"))


integration = pytest.mark.skipif(
    not _has_hindsight_credentials(),
    reason="HINDSIGHT_API_KEY not set — skipping integration test.",
)


@integration
class TestHindsightIntegration:
    """Live Hindsight Cloud integration tests.

    These tests require:
      - HINDSIGHT_API_URL set or the configured default
      - HINDSIGHT_API_KEY set to a valid key
      - HINDSIGHT_BANK_ID set or the configured default
    """

    def _make_client(self):
        from backend.app.hindsight import HindsightClient

        return HindsightClient()

    def test_retain_succeeds(self):
        """Retain request succeeds with valid credentials."""
        client = self._make_client()

        result = client.retain(
            content=SYNTHETIC_EXPERIENCE
        )

        assert result.success, (
            "Retain did not confirm success"
        )

        print("\nHindsight Retain: SUCCESS")
        print("Experience: CASE-001")
        print(f"Bank: {client._bank_id}")

    def test_recall_retrieves_experience(self):
        """Recall retrieves the retained experience."""
        client = self._make_client()

        # Ensure the experience is present.
        client.retain(
            content=SYNTHETIC_EXPERIENCE
        )

        result = client.recall(
            query=RECALL_QUERY
        )

        assert len(result.results) > 0, (
            "Recall returned no results — expected CASE-001."
        )

        combined = " ".join(
            result.results
        ).lower()

        assert any(
            marker in combined
            for marker in [
                "case-001",
                "brk-204",
                "apex",
                "surface crack",
            ]
        ), (
            "Recalled content does not reference "
            f"the test experience. Got: {combined[:300]}"
        )

        print("\nHindsight Recall: SUCCESS")
        print(
            f"Results: {len(result.results)}"
        )

    def test_reflect_reasons_over_experience(self):
        """Reflect processes the retained experience."""
        client = self._make_client()

        # Ensure the experience is present.
        client.retain(
            content=SYNTHETIC_EXPERIENCE
        )

        result = client.reflect(
            query=REFLECT_QUERY
        )

        assert result.text, (
            "Reflect returned empty text."
        )

        text_lower = result.text.lower()

        assert any(
            term in text_lower
            for term in [
                "forming pressure",
                "corrective",
                "inspection",
                "die",
            ]
        ), (
            "Reflection does not reference the "
            "corrective action. "
            f"Got: {result.text[:300]}"
        )

        print("\nHindsight Reflect: SUCCESS")
        print(
            f"Reflection excerpt: {result.text[:200]}..."
        )