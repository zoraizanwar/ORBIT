# ORBIT: AI Intelligence Architecture & Grounded Prompt Engineering

## 1. Core Paradigm: AI as Structured Synthesizer, Never Analytical Source of Truth

In ORBIT, Large Language Models (LLMs) operate strictly at **Epistemic Level 5 (AI Interpretation)**. The AI layer is architecturally decoupled from spatial computation and is strictly forbidden from generating or mutating authoritative physical metrics.

```
+-----------------------------------------------------------------------------------+
|               DETERMINISTIC ANALYTICAL ENGINE (Python + PostGIS)                  |
| - Calculates exact geodesic areas (e.g. affected_area_km2 = 14.23)               |
| - Measures spectral index deltas (e.g. dNDVI_mean = -0.38)                        |
| - Extracts discrete spatiotemporal events (e.g. Road expansion 2022-2024)         |
| - Collects telemetry provenance (e.g. Sentinel-2A scene S2A_MSIL2A_20230715...)  |
+-----------------------------------------+-----------------------------------------+
                                          | Compiles into Immutable JSON Fact Sheet
                                          v
+-----------------------------------------------------------------------------------+
|                        GROUNDED PROMPT COMPILER                                   |
| - Injects verified fact payload into strict System Context                        |
| - Enforces JSON Schema response constraints                                       |
| - Sets temperature to 0.0 (maximum determinism)                                   |
+-----------------------------------------+-----------------------------------------+
                                          | Strict API Request
                                          v
+-----------------------------------------------------------------------------------+
|                          LLM INFERENCE ENGINE                                     |
| (Local: Llama-3-70B / Mistral-Large via Ollama/vLLM OR Commercial: Gemini/Claude) |
+-----------------------------------------+-----------------------------------------+
                                          | Structured Response
                                          v
+-----------------------------------------------------------------------------------+
|                     VALIDATION & ANTI-HALLUCINATION GATE                          |
| - Cross-checks every output number against the input Fact Sheet                   |
| - Validates JSON schema compliance (Pydantic validator)                           |
| - Flags any discrepancies with immediate rejection and fallback assertion         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Structured Evidence Injection Schema (Fact Sheet)

Prior to invoking the LLM, the analytical backend serializes the verified state into an immutable context payload:

```json
{
  "investigation_id": "8f7e2a1b-3c4d-5e6f-7a8b-9c0d1e2f3a4b",
  "aoi_name": "Lake Urmia Southern Basin",
  "bounding_coordinates": [
    {"lat": 37.15, "lon": 45.40},
    {"lat": 37.45, "lon": 45.85}
  ],
  "time_window": {
    "baseline_date": "2018-07-22T08:15:00Z",
    "comparison_date": "2024-07-20T08:18:00Z",
    "baseline_scene_id": "S2A_MSIL2A_20180722T081501_N0206_R064_T38SMG_20180722T104522",
    "comparison_scene_id": "S2B_MSIL2A_20240720T081829_N0510_R064_T38SMG_20240720T121245"
  },
  "authoritative_measurements": [
    {
      "metric_name": "water_surface_area_baseline_km2",
      "value": 1845.20,
      "unit": "km2",
      "epistemic_level": "CALCULATED",
      "confidence": 0.96,
      "method": "PostGIS ST_Area over MNDWI > 0.0 threshold"
    },
    {
      "metric_name": "water_surface_area_comparison_km2",
      "value": 812.45,
      "unit": "km2",
      "epistemic_level": "CALCULATED",
      "confidence": 0.94,
      "method": "PostGIS ST_Area over MNDWI > 0.0 threshold"
    },
    {
      "metric_name": "net_water_loss_km2",
      "value": 1032.75,
      "unit": "km2",
      "epistemic_level": "CALCULATED",
      "confidence": 0.95,
      "method": "Direct difference of baseline and comparison surface area"
    },
    {
      "metric_name": "water_loss_percentage",
      "value": 55.97,
      "unit": "percent",
      "epistemic_level": "CALCULATED",
      "confidence": 0.95,
      "method": "(net_water_loss / baseline_water) * 100"
    }
  ],
  "discrete_events": [
    {
      "event_id": "EVT-2021-049",
      "title": "Desiccation of Southern Basin Mudflats",
      "first_observed": "2021-08-10",
      "last_observed": "2024-07-20",
      "affected_area_km2": 420.10,
      "category": "HYDROLOGICAL_DESICCATION"
    }
  ],
  "sensor_limitations": [
    "Sentinel-2 optical sensors cannot penetrate seasonal cloud cover during November-March",
    "Sub-surface salt crust moisture may slightly skew optical MNDWI water classification"
  ]
}
```

---

## 3. Grounded Intelligence System Prompt Specification

```text
YOU ARE ORBIT-INTEL: THE FORMAL INTELLIGENCE SYNTHESIS ENGINE OF THE ORBIT GEOSPATIAL PLATFORM.

YOUR MISSION:
Synthesize an executive intelligence brief based EXCLUSIVELY on the provided JSON Fact Sheet.

ABSOLUTE INVARIANT RULES:
1. IMMUTABLE NUMERICAL VALUES: You MUST use the exact numerical values provided in 'authoritative_measurements'. You are STRICTLY FORBIDDEN from rounding differently, re-calculating, or fabricating alternative numbers.
2. NO HALLUCINATION OF CAUSES: If the Fact Sheet shows water loss of 1032.75 km², you may describe the measured physical desiccation. You must NOT assert an unproven political or industrial cause unless documented in verified historical records.
3. EXPLICIT UNCERTAINTY: If sensor limitations or cloud cover are reported, you must explicitly highlight them in the Limitations section.
4. EPISTEMIC TAGGING: Every conclusion or narrative paragraph must cite the underlying measurement metric name and sensor scene ID.
5. INSUFFICIENT EVIDENCE RULE: If data is missing for any year or parameter, write exactly: "Insufficient evidence for reliable classification."

RESPONSE FORMAT:
You must output a single, valid JSON document adhering strictly to the OrbitIntelligenceReport schema.
```

---

## 4. Anti-Hallucination & Numerical Validation Gate

Before an AI-generated briefing is saved or presented to the user, the **Validation Gate** runs an automated AST/Regex verification pass:

```python
import re
from typing import Dict, Any, List

class AIOutputVerificationError(Exception):
    pass

def verify_ai_briefing(fact_sheet: Dict[str, Any], ai_response_text: str) -> bool:
    """Verifies that no ungrounded numbers appear in AI narrative and all claimed metrics match fact sheet."""
    # Extract all authoritative numbers from fact sheet
    allowed_numbers = set()
    for m in fact_sheet.get("authoritative_measurements", []):
        val = m["value"]
        allowed_numbers.add(f"{val:.2f}")
        allowed_numbers.add(f"{val:.1f}")
        allowed_numbers.add(f"{int(val)}")
        allowed_numbers.add(str(val))

    # Scan for numerical claims in the narrative
    found_floats = re.findall(r'\b\d+\.\d+\b', ai_response_text)
    for num_str in found_floats:
        val = float(num_str)
        # Check if number matches any allowable measurement, percentage, coordinate, or year
        is_known = any(abs(val - m["value"]) < 0.05 for m in fact_sheet.get("authoritative_measurements", []))
        is_year = 1970 <= val <= 2030
        if not is_known and not is_year:
            # Log verification anomaly
            raise AIOutputVerificationError(
                f"Validation Gate Alert: Number {num_str} in AI narrative is not grounded in authoritative measurements."
            )
    return True
```
