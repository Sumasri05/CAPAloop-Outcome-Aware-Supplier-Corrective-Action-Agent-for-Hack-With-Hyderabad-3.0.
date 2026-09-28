import json
import urllib.request

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

def main():
    print("=== 1. Testing Seed Endpoint via Vite Proxy ===")
    seed_res = post_json("http://localhost:5173/api/v1/seed", {})
    print("Seed status:", seed_res.get("status"), "Total seeded:", seed_res.get("total"))

    print("\n=== 2. Testing Defect Analysis via Vite Proxy ===")
    defect_payload = {
        "supplier": "Apex Components",
        "part_number": "BRK-204",
        "defect_type": "Surface cracks",
        "severity": "major",
        "manufacturing_process": "Metal stamping",
        "description": "Surface cracks appeared after die setup change.",
        "root_cause_hypothesis": "Excessive forming pressure.",
    }
    analyze_res = post_json("http://localhost:5173/api/v1/defects/analyze", defect_payload)
    defect_id = analyze_res["defect_id"]
    print("Defect ID:", defect_id)
    print("Cases found:", analyze_res["historical_cases_found"])
    print("Grade:", analyze_res["recommendation"]["evidence_grade"])
    print("Recommendation:", analyze_res["recommendation"]["corrective_action"][:70], "...")

    print("\n=== 3. Testing Outcome Recording via Vite Proxy ===")
    outcome_payload = {
        "defect_id": defect_id,
        "corrective_action_taken": "Adjusted forming pressure to 380 kN and added first-article inspection.",
        "verification_period": "14 production days",
        "measurement_before": "7.8% defect rate",
        "measurement_after": "0.7% defect rate",
        "outcome": "successful",
        "recurrence": "Zero recurrence observed.",
        "notes": "Verified on 14-day production batch.",
        "evidence_quality": "A",
    }
    outcome_res = post_json("http://localhost:5173/api/v1/defects/outcome", outcome_payload)
    print("Outcome status:", outcome_res.get("status"), "Hindsight retained:", outcome_res.get("hindsight_retained"))

    print("\n=== 4. Testing Timeline Endpoint via Vite Proxy ===")
    timeline_res = get_json(f"http://localhost:5173/api/v1/defects/{defect_id}/timeline")
    print("Timeline events count:", len(timeline_res.get("events", [])))
    for e in timeline_res.get("events", []):
        print(f"  - [{e['event_type']}] {e['summary'][:60]}...")

    print("\n=== 5. Testing Learning: Re-analyzing Similar Defect ===")
    reanalyze_res = post_json("http://localhost:5173/api/v1/defects/analyze", defect_payload)
    print("Re-analysis Defect ID:", reanalyze_res["defect_id"])
    print("Cases found after learning:", reanalyze_res["historical_cases_found"])
    print("Grade:", reanalyze_res["recommendation"]["evidence_grade"])
    print("\n=== All Steps Succeeded via Vite Proxy! ===")

if __name__ == "__main__":
    main()
