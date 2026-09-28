"""
CAPAloop — Seed data.

10 SYNTHETIC supplier-quality experiences for demonstration.
These are clearly labelled as synthetic demo data.

The dataset covers:
  1. Successful corrective action
  2. Failed corrective action
  3. Partial success
  4. Recurring defect
  5. Contradictory case (same defect, different outcome)
  6. Similar supplier, different process
  7. Same defect, different part
  8. Strong historical match
  9. Weak historical match
  10. No-precedent scenario (exotic defect)
"""

from __future__ import annotations

SEED_EXPERIENCES: list[str] = [
    # -----------------------------------------------------------------------
    # 1. SUCCESSFUL corrective action — strong evidence
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-001
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Surface cracks appeared on brake mounting brackets after a die setup change \
on the metal stamping line. 23 defective parts were identified during \
in-process inspection over a single shift.

Root-cause hypothesis:
Excessive forming pressure combined with die alignment drift after setup.

Corrective action:
Adjusted forming pressure from 420 kN to 380 kN and added mandatory \
first-article inspection (3 pieces) after every die change.

Implementation date: 2025-03-15
Verification period: 14 production days

Follow-up measurement:
Defect rate reduced from 7.8% to 0.9%.

Outcome: Successful
Recurrence: No recurrence during the 14-day verification period.

Evidence quality: A
Evidence limitation: The intervention was associated with successful \
resolution in this historical context; causality has not been established.
""",

    # -----------------------------------------------------------------------
    # 2. FAILED corrective action
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-002
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Surface cracks reappeared after a tooling vendor supplied replacement die \
inserts. Initial assumption was that the issue was identical to SEED-001.

Root-cause hypothesis:
Same as SEED-001 — forming pressure too high.

Corrective action:
Reduced forming pressure to 360 kN without first-article inspection change.

Implementation date: 2025-06-10
Verification period: 7 production days

Follow-up measurement:
Defect rate remained at 6.2% — no meaningful improvement.

Outcome: Failed
Recurrence: Defect continued at elevated rate.

Evidence quality: B
Evidence limitation: Pressure reduction alone was not sufficient. \
The die insert material quality was not investigated. \
Association only — causality not established.
""",

    # -----------------------------------------------------------------------
    # 3. PARTIAL success
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-003
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Follow-up to SEED-002. Quality team investigated die insert hardness \
and found incoming die inserts were below specification (58 HRC vs. 62 HRC).

Root-cause hypothesis:
Sub-specification die insert hardness causing premature wear and surface \
cracking during forming.

Corrective action:
Added incoming hardness inspection for die inserts (minimum 61 HRC) \
and maintained reduced forming pressure at 370 kN.

Implementation date: 2025-07-22
Verification period: 14 production days

Follow-up measurement:
Defect rate reduced from 6.2% to 2.1%. Improvement but not to target (<1%).

Outcome: Partial
Recurrence: Sporadic cracks still observed (2-3 per shift).

Evidence quality: B
Evidence limitation: Improvement observed but target not met. \
Multiple variables changed simultaneously.
""",

    # -----------------------------------------------------------------------
    # 4. RECURRING defect
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-004
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Three months after SEED-003, surface cracks reappeared during a high-volume \
production run. Investigation revealed that the incoming die insert \
inspection had been skipped during a weekend overtime shift.

Root-cause hypothesis:
Process discipline failure — incoming inspection bypassed under \
production pressure.

Corrective action:
Implemented automated hardness check fixture at die storage area. \
Die inserts cannot be released without recorded hardness measurement.

Implementation date: 2025-11-05
Verification period: 30 production days

Follow-up measurement:
Defect rate stabilized at 0.4%.

Outcome: Successful
Recurrence: No recurrence during 30-day extended verification.

Evidence quality: A
Evidence limitation: Long verification period strengthens confidence. \
However, association does not establish causality.
""",

    # -----------------------------------------------------------------------
    # 5. CONTRADICTORY case — same defect, opposite outcome
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-005
Supplier: Meridian Metals
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Similar surface cracks on BRK-204, but from a different supplier \
(Meridian Metals) using a different stamping press (800-ton vs. Apex's \
500-ton press).

Root-cause hypothesis:
Forming pressure too high on the 800-ton press.

Corrective action:
Reduced forming pressure and added first-article inspection \
(same approach as SEED-001).

Implementation date: 2025-05-01
Verification period: 14 production days

Follow-up measurement:
Defect rate increased from 5.1% to 5.8% after pressure reduction. \
The corrective action made the problem slightly worse.

Outcome: Failed
Recurrence: Defect worsened.

Evidence quality: B
Evidence limitation: The same corrective action that succeeded at Apex \
failed at Meridian Metals. Root cause may be supplier-specific (material, \
press characteristics). This contradicts SEED-001.
""",

    # -----------------------------------------------------------------------
    # 6. Similar supplier, DIFFERENT process
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-006
Supplier: Apex Components
Part: HSG-112
Defect: Porosity
Severity: Major
Manufacturing Process: Die casting

Context:
Porosity defects in aluminum die-cast housings from Apex Components. \
Not related to metal stamping but same supplier.

Root-cause hypothesis:
Insufficient degassing of molten aluminum and excessive gate speed.

Corrective action:
Extended degassing cycle from 8 min to 12 min, reduced gate speed \
by 15%, and added X-ray inspection for critical housings.

Implementation date: 2025-04-18
Verification period: 21 production days

Follow-up measurement:
Porosity rejection rate reduced from 12.3% to 1.8%.

Outcome: Successful
Recurrence: No recurrence during verification period.

Evidence quality: A
Evidence limitation: Different manufacturing process (die casting vs. \
metal stamping). Corrective action is process-specific.
""",

    # -----------------------------------------------------------------------
    # 7. Same defect, DIFFERENT part
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-007
Supplier: Apex Components
Part: ARM-508
Defect: Surface cracks
Severity: Minor
Manufacturing Process: Metal stamping

Context:
Surface cracks on control arm brackets (ARM-508), a different part \
than BRK-204 but same supplier and same stamping process.

Root-cause hypothesis:
Material batch variation — tensile strength at upper specification limit.

Corrective action:
Tightened incoming material specification for tensile strength \
(max 580 MPa vs. previous 620 MPa) and adjusted blank holder force.

Implementation date: 2025-08-12
Verification period: 14 production days

Follow-up measurement:
Defect rate reduced from 4.5% to 0.6%.

Outcome: Successful
Recurrence: No recurrence.

Evidence quality: A
Evidence limitation: Different part geometry. Corrective action may \
not transfer directly to BRK-204.
""",

    # -----------------------------------------------------------------------
    # 8. STRONG historical match
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-008
Supplier: Apex Components
Part: BRK-204
Defect: Surface cracks
Severity: Major
Manufacturing Process: Metal stamping

Context:
Comprehensive resolution combining lessons from SEED-001 through SEED-004. \
Full root-cause analysis performed using 5-Why and fishbone diagram.

Root-cause hypothesis:
Multi-factor: (1) forming pressure sensitivity, (2) die insert hardness, \
(3) process discipline on incoming inspection.

Corrective action:
1. Forming pressure set to 380 kN with documented tolerance band (±10 kN).
2. Automated die insert hardness verification (min 61 HRC).
3. First-article inspection (5 pieces) mandatory after every die change.
4. Process control chart for crack defect rate with action limits.

Implementation date: 2025-12-01
Verification period: 30 production days

Follow-up measurement:
Defect rate reduced from 7.8% to 0.3%. Best result achieved.

Outcome: Successful
Recurrence: No recurrence during 30-day verification or subsequent \
60-day extended monitoring.

Evidence quality: A
Evidence limitation: Comprehensive multi-factor corrective action. \
Difficult to isolate which individual factor contributed most. \
Association does not establish causality.
""",

    # -----------------------------------------------------------------------
    # 9. WEAK historical match
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-009
Supplier: TechForm Industries
Part: PLT-330
Defect: Micro-fractures
Severity: Critical
Manufacturing Process: Cold forging

Context:
Micro-fractures detected in cold-forged pivot plates. Different supplier, \
different part, different process, but defect category (cracking) \
has surface similarity to BRK-204 surface cracks.

Root-cause hypothesis:
Excessive strain rate during cold forging.

Corrective action:
Reduced ram speed by 20% and added intermediate annealing step.

Implementation date: 2025-09-05
Verification period: 10 production days

Follow-up measurement:
Fracture rate reduced from 3.2% to 0.8%.

Outcome: Successful
Recurrence: Minor recurrence at 0.5% after 45 days.

Evidence quality: C
Evidence limitation: Different supplier, part, and process. \
Relevance to surface cracks on stamped parts is uncertain. \
Short verification period. Minor recurrence noted.
""",

    # -----------------------------------------------------------------------
    # 10. NO-PRECEDENT scenario (exotic defect)
    # -----------------------------------------------------------------------
    """\
[SYNTHETIC DEMO DATA — CAPAloop Seed Experience]

Experience ID: SEED-010
Supplier: Apex Components
Part: SHF-720
Defect: Hydrogen embrittlement
Severity: Critical
Manufacturing Process: Electroplating

Context:
Hydrogen embrittlement detected in electroplated shaft assemblies. \
Parts passed dimensional inspection but failed under sustained load testing. \
This is an uncommon failure mode for this supplier.

Root-cause hypothesis:
Inadequate baking cycle after zinc electroplating, allowing absorbed \
hydrogen to remain in the steel substrate.

Corrective action:
Extended post-plating bake from 4 hours to 8 hours at 190°C. \
Added hydrogen embrittlement test (sustained load at 75% UTS for 200 hours) \
to incoming inspection plan.

Implementation date: 2025-10-20
Verification period: 21 production days (plus 200-hour load test per batch)

Follow-up measurement:
Zero failures in sustained load testing after corrective action.

Outcome: Successful
Recurrence: No recurrence. All batches passed 200-hour load test.

Evidence quality: B
Evidence limitation: Rare failure mode. Only one historical case. \
Evidence is supplier-specific and may not apply to other plating vendors.
""",
]


def get_seed_experiences() -> list[str]:
    """Return the list of synthetic seed experiences."""
    return SEED_EXPERIENCES


def seed_to_hindsight(client) -> list[str]:
    """Retain all seed experiences in Hindsight.

    Args:
        client: An initialised HindsightClient.

    Returns:
        List of experience IDs that were successfully retained.
    """
    import re
    retained: list[str] = []

    for exp_text in SEED_EXPERIENCES:
        match = re.search(r"Experience ID:\s*(\S+)", exp_text)
        exp_id = match.group(1) if match else "UNKNOWN"

        try:
            result = client.retain(content=exp_text)
            if result.success:
                retained.append(exp_id)
                print(f"  ✓ Retained: {exp_id}")
            else:
                print(f"  ✗ Failed: {exp_id}")
        except Exception as exc:
            print(f"  ✗ Error retaining {exp_id}: {exc}")

    return retained


async def aseed_to_hindsight(client) -> list[str]:
    """Retain all seed experiences in Hindsight asynchronously.

    Args:
        client: An initialised HindsightClient.

    Returns:
        List of experience IDs that were successfully retained.
    """
    import re
    retained: list[str] = []

    for exp_text in SEED_EXPERIENCES:
        match = re.search(r"Experience ID:\s*(\S+)", exp_text)
        exp_id = match.group(1) if match else "UNKNOWN"

        try:
            result = await client.aretain(content=exp_text)
            if result.success:
                retained.append(exp_id)
                print(f"  ✓ Retained: {exp_id}")
            else:
                print(f"  ✗ Failed: {exp_id}")
        except Exception as exc:
            print(f"  ✗ Error retaining {exp_id}: {exc}")

    return retained

