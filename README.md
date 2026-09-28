# CAPAloop — Outcome-Aware Supplier Corrective-Action Agent

> **Hack With Hyderabad 3.0**  
> An outcome-aware supplier corrective-action decision-support agent powered by Hindsight Cloud long-term memory.

---

## Problem

Supplier defects frequently recur in manufacturing because quality and engineering teams do not systematically learn from previous corrective actions (CAPAs) and their verified outcomes. Historical resolutions, failure modes, and verification results often remain trapped in static spreadsheets or siloed ticketing systems. As a result:

- Engineers repeatedly attempt trial-and-error fixes that previously failed under similar conditions.
- Successful corrective actions are not surfaced when identical failure modes reappear on different production lines or suppliers.
- Teams lack visibility into whether past corrective actions produced sustained recurrence prevention or merely temporary symptom relief.

## Solution

**CAPAloop** closes the loop on supplier quality management. By integrating **Hindsight Cloud** long-term memory, CAPAloop remembers verified supplier quality experiences, recalls relevant historical precedents upon defect intake, and reflects over past outcomes (successful, partial, or failed) to provide evidence-backed corrective recommendations and structured verification plans.

---

## The Hindsight Role

Hindsight Cloud acts as the persistent cognitive memory bank for CAPAloop:

- **Recall**: Semantically retrieves relevant historical experiences based on supplier, part category, manufacturing process, and defect characteristics.
- **Reflect**: Synthesizes reasoning across multiple historical experiences to generate grounded recommendations, identify contradictory outcomes, and cite evidence strength.
- **Retain**: Permanently stores newly verified defect-action-outcome records into memory once verification criteria are met.

### The Closed-Loop Workflow: Recall → Recommend → Verify → Retain → Learn

```text
┌────────────────┐     ┌──────────────┐     ┌─────────────┐
│ 1. Defect      │ ──> │  2. Recall   │ ──> │ 3. Reflect  │
│    Intake      │     │  (Hindsight) │     │ (Recommend) │
└────────────────┘     └──────────────┘     └─────────────┘
                                                   │
┌────────────────┐     ┌──────────────┐            ▼
│ 5. Learn &     │ <── │  4. Retain   │ <── ┌─────────────┐
│    Close Loop  │     │  (Hindsight) │     │ 4. Verify   │
│ (Re-analysis)  │     │  (Verified)  │     │    Outcome  │
└────────────────┘     └──────────────┘     └─────────────┘
```

1. **Recall**: When a new defect occurs, CAPAloop retrieves historical cases from Hindsight.
2. **Recommend**: CAPAloop reflects over recalled outcomes to suggest proven corrective actions with confidence grading (Grade A/B/C) and highlighted limitations.
3. **Verify**: A structured verification period (e.g., 14–30 production days) and measurable targets (e.g., defect rate reduction) are tracked.
4. **Retain**: Upon verification completion, the verified outcome (successful, partial, or failed) is retained in Hindsight.
5. **Learn**: The newly retained experience immediately enriches future recall and reflection queries.

---

## Key Features

- **Outcome-Aware Recommendations**: Prioritizes actions with historically verified recurrence prevention over unverified fixes.
- **Evidence Quality Grading**: Assigns confidence levels (Grade A, B, or C) based on precedent verification rigor.
- **Contradiction & Limitation Detection**: Highlights cases where an action succeeded at one supplier but failed at another.
- **Structured Verification Planning**: Generates required observation periods, sample sizes, and quantitative success thresholds.
- **Interactive Judge Demo**: A live side-by-side walkthrough demonstrating the complete learning loop from pre-verification baseline to post-retention memory retrieval.

---

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Frontend UI                          │
│        (React 18 + Vite + Vanilla CSS System)           │
└───────────────────────────┬─────────────────────────────┘
                            │ REST API (JSON)
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                        │
│   ├── /api/v1/defects/analyze   (Recall + Reflect)      │
│   ├── /api/v1/defects/verify    (Outcome Verification)  │
│   ├── /api/v1/timeline          (Audit Trail)           │
│   ├── /retain, /recall, /reflect (Hindsight Primitives) │
│   └── /health                   (System & Cloud Health) │
└───────────────────────────┬─────────────────────────────┘
                            │ Async HTTPS
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 Hindsight Cloud Engine                  │
│       ├── Retain  — Store verified outcome records      │
│       ├── Recall  — Contextual vector & keyword search  │
│       └── Reflect — Multi-experience synthesis         │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn, HTTPX
- **Memory Engine**: Hindsight Cloud API (`hindsight-client` / REST client)
- **Frontend**: React 18, Vite, Vanilla CSS design system
- **Testing**: Pytest, pytest-asyncio, HTTPX TestClient

---

## Getting Started Locally

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Hindsight Cloud API Key ([hindsight.vectorize.io](https://hindsight.vectorize.io))

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/Sumasri05/CAPAloop-Outcome-Aware-Supplier-Corrective-Action-Agent-for-Hack-With-Hyderabad-3.0..git
cd CAPAloop-Outcome-Aware-Supplier-Corrective-Action-Agent-for-Hack-With-Hyderabad-3.0.

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `.env` with your Hindsight Cloud credentials:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_BANK_ID=defect-learning-demo
```

> **Security Note:** Never commit your `.env` file. It is excluded via `.gitignore`.

Start the backend server:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend health:

```bash
curl http://localhost:8000/health
```

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Running Tests

### Backend Test Suite (58 tests)

```bash
# Run all unit and integration tests
pytest backend/tests -v
```

All 58 tests cover:
- Hindsight Retain, Recall, and Reflect operations
- Error handling, timeouts, and fallback modes
- Complete CAPA workflow: Defect intake → Analysis → Verification → Retain → Timeline audit
- End-to-end proxy endpoints and health probes

### Frontend Production Build

```bash
cd frontend
npm run build
```

---

## Live Judge Demo Flow

The frontend includes an automated **Judge Demo** view that executes the entire learning cycle in real time against Hindsight Cloud:

1. **Step 1 — Initial Defect Analysis**: Submits an unverified defect instance. CAPAloop recalls relevant historical background context while noting that this specific defect instance has no verified resolution yet.
2. **Step 2 — Action & Outcome Verification**: Simulates a 14-day verification window where forming pressures are calibrated, resulting in an 88% defect reduction (from 7.8% down to 0.9%) with zero recurrence.
3. **Step 3 — Retain into Hindsight**: Retains the verified defect-action-outcome tuple into Hindsight Cloud memory.
4. **Step 4 — Re-Analysis & Learning Verification**: Re-analyzes the failure mode. CAPAloop immediately recalls the newly retained experience, upgrading recommendation confidence and confirming that the agent has learned from the verified outcome.

---

## Disclaimers & Limitations

### Synthetic Data Disclaimer
All defect records, supplier names (e.g., "Apex Components"), part serial numbers, manufacturing defect descriptions, and numerical outcome measurements in this repository and demo are **synthetic data** generated strictly for hackathon prototyping, testing, and evaluation. They do not represent real-world proprietary manufacturing records.

### Causality Limitation
Outcome awareness in CAPAloop identifies **observed historical associations** between implemented corrective actions and defect rate reductions. These correlations do not constitute definitive mathematical or physical proof of causation, as confounding manufacturing variables (e.g., raw material batches, tooling wear, seasonal ambient temperature, operator rotations) may also affect production quality.

---

## License

This project is created for **Hack With Hyderabad 3.0**.
