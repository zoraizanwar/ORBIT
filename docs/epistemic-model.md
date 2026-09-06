# ORBIT Epistemic Classification Model & Anti-Hallucination Framework

## 1. The 5-Tier Epistemic Ladder

ORBIT prevents AI hallucination and false confidence by strictly partitioning all platform knowledge across five mutually exclusive epistemic levels:

| Level | Identifier | Description | Verification Method | Mutation / Upgrade Rule |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `OBSERVED` | Raw sensor telemetry, calibrated surface reflectance, OSM road vectors. | Direct sensor telemetry or authoritative registry | **Immutable**. Cannot be created by software logic. |
| **1** | `CALCULATED` | Deterministic mathematical transforms (NDVI, NDWI, surface area, delta). | Deterministic formula execution against `OBSERVED` inputs | Can be recomputed with identical numerical results. |
| **2** | `DETECTED` | Rule-based spatial/temporal events (e.g. Otsu change clusters, road buffer correlations). | Multi-sensor threshold confirmation & spatial intersection | Derived strictly from `CALCULATED` / `OBSERVED` data. |
| **3** | `PREDICTED` | Statistical forecasts and forward-looking time-series projections. | Extrapolated trend models with explicit uncertainty intervals | Must clearly state statistical bounds; never present as current truth. |
| **4** | `AI_INTERPRETED`| Natural-language intelligence synthesis, claims, and decision support. | Grounded reasoning engine citing specific evidence IDs | **STRICTLY PROHIBITED** from upgrading any claim to `OBSERVED`, `CALCULATED`, or `DETECTED`. |

---

## 2. Inviolable Anti-Hallucination Rules

### Rule 1: No Upward Epistemic Promotion
AI interpretation models (`AI_INTERPRETED`) may never classify their synthesized findings as `OBSERVED` or `CALCULATED`. If an LLM suggests a phenomenon (e.g., "Illegal logging detected in Sector 4"), the claim remains `AI_INTERPRETED` until independently verified by ground-truth sensor telemetry or calibrated deterministic algorithms.

### Rule 2: Mandatory Citation Grounding
Every claim generated in an intelligence summary must cite at least one valid `evidence_id` present in the accompanying `EvidencePackage`. Uncited claims are rejected by the platform's assertion validator before ingestion.

### Rule 3: Contradiction Degradation
If two independent sensors provide conflicting observations (e.g., Optical NDVI shows -0.45 drop while SAR Backscatter shows no surface roughness alteration), the rule engine flags a contradiction:
- Evidence strength is automatically degraded from `STRONG` to `INSUFFICIENT` or `CONTRADICTED`.
- An explicit **Uncertainty & Contradiction Statement** is injected into the intelligence dossier.
- The platform blocks confident automated action proposals.

---

## 3. Evidence Strength Grading

1. **`STRONG`**: Multi-sensor corroboration (e.g., Optical + SAR), high valid pixel percentage (>90%), cloud cover <10%, spatial road correlation within buffer distance.
2. **`MODERATE`**: Single sensor confirmation with clear signal delta, minimal cloud interference.
3. **`WEAK`**: Single sensor observation with partial cloud cover or borderline statistical significance.
4. **`INSUFFICIENT`**: Missing baseline observations, high noise, or conflicting cross-modality signals.
