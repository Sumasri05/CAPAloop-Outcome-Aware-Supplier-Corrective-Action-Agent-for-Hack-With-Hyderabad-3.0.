"""
CAPAloop — FastAPI application.

Phase 2: Outcome-aware supplier corrective-action agent.

Endpoints:
  GET  /health                              — liveness + Hindsight status
  POST /retain                              — store experience (Phase 1)
  POST /recall                              — search experiences (Phase 1)
  POST /reflect                             — synthesise reasoning (Phase 1)
  POST /api/defects/analyze                 — analyze a new defect (Phase 2)
  POST /api/experiences/{id}/outcome        — record verification outcome
  GET  /api/learning/timeline               — learning event timeline
  POST /api/seed                            — seed demo experiences
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import ConfigurationError, load_settings
from .hindsight import (
    HindsightAuthError,
    HindsightBankError,
    HindsightClient,
    HindsightConnectionError,
    HindsightError,
    HindsightRecallError,
    HindsightReflectError,
    HindsightRetainError,
)

logger = logging.getLogger("capaloop")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------

_hindsight: HindsightClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise shared resources on startup."""
    global _hindsight
    try:
        _hindsight = HindsightClient()
        logger.info("Hindsight client ready.")
    except ConfigurationError as exc:
        logger.warning("Hindsight not configured: %s", exc)
        _hindsight = None
    except HindsightConnectionError as exc:
        logger.warning("Hindsight unreachable at startup: %s", exc)
        _hindsight = None
    yield
    _hindsight = None


app = FastAPI(
    title="CAPAloop",
    description=(
        "Outcome-aware supplier corrective-action agent — "
        "learns from verified historical quality experiences using Hindsight."
    ),
    version="0.2.0",
    lifespan=lifespan,
)


def _get_client() -> HindsightClient:
    """Return the initialised Hindsight client or raise 503."""
    if _hindsight is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Hindsight client is not available. "
                "Check server logs for configuration or connection errors."
            ),
        )
    return _hindsight


# ---------------------------------------------------------------------------
# Include Phase 2 API routers
# ---------------------------------------------------------------------------

from .api.defects import router as defects_router
from .api.experiences import router as experiences_router
from .api.learning import router as learning_router

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(defects_router)
app.include_router(experiences_router)
app.include_router(learning_router)

from .models import AnalysisResponse, DefectInput, OutcomeInput, OutcomeResponse, TimelineResponse

@app.post("/api/v1/defects/analyze", response_model=AnalysisResponse, tags=["v1"])
async def v1_analyze(defect: DefectInput) -> AnalysisResponse:
    from .api.defects import analyze
    return await analyze(defect)

@app.post("/api/v1/defects/outcome", response_model=OutcomeResponse, tags=["v1"])
async def v1_outcome(body: OutcomeInput) -> OutcomeResponse:
    from .api.defects import record_defect_outcome
    return await record_defect_outcome(body)

@app.get("/api/v1/defects/{defect_id}/timeline", response_model=TimelineResponse, tags=["v1"])
async def v1_timeline(defect_id: str) -> TimelineResponse:
    from .api.defects import get_defect_timeline
    return await get_defect_timeline(defect_id)

@app.post("/api/v1/seed", tags=["v1"])
async def v1_seed():
    return await seed_experiences()


# ---------------------------------------------------------------------------
# Phase 1 schemas (preserved for backward compatibility)
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    hindsight: str = "unknown"


class RetainRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Experience text to retain.")


class RetainResponse(BaseModel):
    status: str
    detail: str


class RecallRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language search query.")


class RecallResponse(BaseModel):
    status: str
    results: list[str]
    count: int


class ReflectRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Reflection prompt.")


class ReflectResponse(BaseModel):
    status: str
    text: str


class SeedResponse(BaseModel):
    status: str
    retained: list[str]
    total: int


# ---------------------------------------------------------------------------
# Phase 1 endpoints (preserved)
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Application liveness check with optional Hindsight connectivity."""
    if _hindsight is None:
        return HealthResponse(status="ok", hindsight="not_configured")
    try:
        if hasattr(_hindsight, "acheck_connection") and inspect.iscoroutinefunction(_hindsight.acheck_connection):
            await _hindsight.acheck_connection()
        else:
            _hindsight.check_connection()
        return HealthResponse(status="ok", hindsight="connected")
    except HindsightAuthError:
        return HealthResponse(status="ok", hindsight="auth_error")
    except HindsightBankError:
        return HealthResponse(status="ok", hindsight="bank_error")
    except HindsightConnectionError:
        return HealthResponse(status="ok", hindsight="unreachable")
    except HindsightError:
        return HealthResponse(status="ok", hindsight="error")


@app.post("/retain", response_model=RetainResponse)
async def retain(body: RetainRequest) -> RetainResponse:
    """Store a supplier-quality experience in Hindsight."""
    client = _get_client()
    try:
        if hasattr(client, "aretain") and inspect.iscoroutinefunction(client.aretain):
            result = await client.aretain(content=body.content)
        else:
            result = client.retain(content=body.content)
        return RetainResponse(status="success", detail=result.detail)
    except HindsightAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HindsightBankError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HindsightConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HindsightRetainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/recall", response_model=RecallResponse)
async def recall(body: RecallRequest) -> RecallResponse:
    """Search historical supplier-quality experiences."""
    client = _get_client()
    try:
        if hasattr(client, "arecall") and inspect.iscoroutinefunction(client.arecall):
            result = await client.arecall(query=body.query)
        else:
            result = client.recall(query=body.query)
        return RecallResponse(
            status="success" if result.results else "no_results",
            results=result.results,
            count=len(result.results),
        )
    except HindsightAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HindsightBankError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HindsightConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HindsightRecallError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/reflect", response_model=ReflectResponse)
async def reflect(body: ReflectRequest) -> ReflectResponse:
    """Synthesise reasoning over historical supplier-quality experiences."""
    client = _get_client()
    try:
        if hasattr(client, "areflect") and inspect.iscoroutinefunction(client.areflect):
            result = await client.areflect(query=body.query)
        else:
            result = client.reflect(query=body.query)
        if not result.text:
            raise HTTPException(
                status_code=500,
                detail="Reflection could not be completed — no response from Hindsight.",
            )
        return ReflectResponse(status="success", text=result.text)
    except HindsightAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HindsightBankError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HindsightConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HindsightReflectError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Reflection could not be completed: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Seed endpoint
# ---------------------------------------------------------------------------

@app.post("/api/seed", response_model=SeedResponse)
async def seed_experiences() -> SeedResponse:
    """Seed synthetic demo experiences into Hindsight.

    This retains 10 synthetic supplier-quality experiences for demo purposes.
    Clearly labelled as synthetic data.
    """
    client = _get_client()
    from .seed import aseed_to_hindsight, seed_to_hindsight
    if hasattr(client, "aretain") and inspect.iscoroutinefunction(client.aretain):
        retained = await aseed_to_hindsight(client)
    else:
        retained = seed_to_hindsight(client)
    return SeedResponse(
        status="success" if retained else "failed",
        retained=retained,
        total=len(retained),
    )
