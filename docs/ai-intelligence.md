# ORBIT Phase 13 — Grounded AI Intelligence Synthesis, Evidence-Based Reporting & Decision Support

## 1. Executive Summary & Epistemic Separation

ORBIT (Geospatial Intelligence & Earth Monitoring Platform) Phase 13 introduces a deterministic, hallucination-resistant Grounded AI Intelligence Synthesis layer. Operating strictly as an explanatory interpretation engine over validated Earth observations, spectral indices, spatial difference masks, corridor clearings, and statistical forecasts, the system produces traceable claims, cross-sensor contradiction assessments, prioritized operational recommendations, and cryptographic intelligence reports.

```
+-----------------------------------------------------------------------------+
|                           ORBIT Epistemic Hierarchy                         |
+-----------------------------------------------------------------------------+
| Level 1: OBSERVED           | Raw sensor telemetry (Sentinel/Landsat), OSM  |
| Level 2: CALCULATED         | Spectral indices (dNDVI, dNDBI), change masks |
| Level 3: DETECTED           | Multi-indicator events, corridor clearances   |
| Level 4: HISTORICAL         | Multi-decadal empirical summaries (1984-2024) |
| Level 5: PREDICTED          | Calibrated linear trend extrapolations        |
| Synthesis: AI_INTERPRETED   | Grounded explanatory synthesis & decision recs|
+-----------------------------------------------------------------------------+
```

### Core Invariants:
1. **Strict Epistemic Separation**: AI-generated synthesis carries `epistemic_level = AI_INTERPRETED`. It is explanatory metadata and never mutates or overwrites raw sensor observations (`OBSERVED`), deterministic metrics (`CALCULATED`), discrete detections (`DETECTED`), or statistical forecasts (`PREDICTED`).
2. **Zero-Fabrication Policy**: The AI never generates ungrounded satellite scenes, synthetic coordinates, fabricated acquisition dates, invented index values, or uncalibrated predictions. When evidence is insufficient, it explicitly returns `INSUFFICIENT_EVIDENCE`.
3. **Adversarial Claim Validation**: Every generated claim undergoes post-generation verification ensuring 100% cited evidence ID existence, exact numerical token alignment, and date interval fidelity.
4. **Anti-Reconciliation Contradiction Handling**: If optical and SAR telemetry diverge, the engine forbids artificial reconciliation, explicitly highlights the contradiction, and downgrades evidence strength to `INSUFFICIENT`.

---

## 2. Grounded Reasoning Pipeline Architecture

```
User / Analyst Request (AOI, Target Run, Intelligence Event)
  │
  ▼
Deterministic Evidence Retriever (Assembles scenes, spectral deltas, masks, roads, forecasts, & edges)
  │
  ▼
Evidence Package Digest (Calculates immutable SHA-256 fingerprint over items and relationship DAG)
  │
  ▼
Prompt Sanitization & Security Boundary (Strips injection characters; injects hard epistemic guardrails)
  │
  ▼
Reasoning Provider (LocalDeterministicReasoner or External OpenAI-Compatible Provider)
  │
  ▼
Adversarial Claim Validator (Verifies evidence ID existence, numerical match, year fidelity, & contradictions)
  │
  ▼
Decision Support Engine (Derives deterministic HIGH/MEDIUM/LOW prioritized recommendations)
  │
  ▼
Cryptographic Provenance Sealing (Attaches SHA-256 calculation fingerprint & audit trace)
  │
  ▼
Report Generation & API Persistence (Stores AIInterpretation, AIClaim, AIRecommendation, & AIReport)
```

---

## 3. Adversarial Claim Validation & Anti-Hallucination Engine

The [`ClaimValidator`](file:///c:/Users/Zuraiz%20Malik/Desktop/ORBIT/backend/app/services/ai/claim_validator.py) acts as a deterministic adversary between model output and final presentation:

1. **Citation Verification**: Every claim must cite $\ge 1$ evidence IDs. Any citation of a non-existent ID results in immediate rejection (`support_status = UNSUPPORTED`).
2. **Numerical Token Matching**: All decimal and integer numbers appearing in the claim text must exist in the underlying evidence items or metadata descriptions (e.g. area $6.85\text{ km}^2$, proximity $85.0\text{ m}$, index delta $-0.24$). Hallucinated numbers trigger validation failure.
3. **Temporal Bounds Check**: Year tokens (e.g. 2023, 2026, 2030) must match evidence timestamps or projection horizons.
4. **Epistemic Invariant Check**: Prohibits claims from describing future extrapolations (`PREDICTED`) as confirmed physical observations (`OBSERVED`).
5. **Contradiction Propagation**: If cited evidence connects to a `CONTRADICTS` relationship edge in the evidence graph, the claim is flagged as `CONTRADICTED` with confidence capped at $0.50$.

---

## 4. Cross-Sensor Contradiction Auditing

When multi-sensor modalities disagree (e.g., optical reflectance indicates canopy deficit while SAR radar amplitude remains invariant), ORBIT enforces epistemic discipline:
- Never suppresses contradictory signals.
- Never manufactures speculative explanations without empirical ground truth.
- Displays prominent uncollapsible `ContradictionBanner` in the UI.
- Automatically generates a `REVIEW_CONTRADICTION` operational recommendation with `HIGH` priority.

---

## 5. Prioritized Operational Decision Support

The decision support engine converts grounded telemetry into prioritized action items:

| Priority | Criteria / Trigger | Example Action |
| :--- | :--- | :--- |
| **HIGH** | Unresolved cross-sensor contradictions or rapid corridor deforestation. | Conduct multi-pass radar coherence audit; deploy UAV ground survey. |
| **MEDIUM** | Active corridor clearance exceeding standard variance threshold. | Perform high-resolution cadastral boundary overlay to verify concession permits. |
| **LOW** | Stable historical baseline with normal seasonal variation. | Maintain standard scheduled satellite surveillance cadence. |

---

## 6. Traceable Intelligence Reports

The [`ReportGenerator`](file:///c:/Users/Zuraiz%20Malik/Desktop/ORBIT/backend/app/services/ai/report_generator.py) produces signed Markdown and JSON intelligence reports containing:
1. Executive Summary & Area Context
2. Epistemic Hierarchy Breakdown
3. Grounded Evidence Claims with Cited IDs
4. Cross-Sensor Contradiction Assessment
5. Spatial & Infrastructure Corridor Context
6. Future Forecast Projections (Level 5: PREDICTED)
7. Operational Decision Support & Prioritized Actions
8. Uncertainty & Methodological Statement
9. Complete Grounded Evidence Inventory Table
10. Cryptographic SHA-256 Provenance Fingerprint

---

## 7. Database Migration & Schema (`0008_grounded_ai_intelligence.py`)

- `intelligence.ai_interpretations`: Primary record of grounded synthesis, summary, statements, and evidence package digest.
- `intelligence.ai_claims`: Individual validated claims with epistemic level, cited evidence IDs, support status, and confidence.
- `intelligence.ai_recommendations`: Operational recommendations with deterministic priority, rationale, and evidence links.
- `intelligence.ai_reports`: Rendered intelligence reports with SHA-256 provenance signatures.

---

## 8. REST API Reference

- `POST /api/v1/ai/evidence/package`: Assembles deterministic evidence package with SHA-256 digest.
- `POST /api/v1/ai/interpret`: Generates grounded AI synthesis with adversarial claim validation.
- `POST /api/v1/ai/claims/validate`: Standalone adversarial claim validation against an evidence package.
- `POST /api/v1/ai/reports/generate`: Generates signed Markdown/JSON reports.
- `POST /api/v1/ai/decision-support`: Generates prioritized operational recommendations.
- `GET /api/v1/ai/interpretations/{id}`: Retrieves saved interpretation by UUID.
- `GET /api/v1/ai/interpretations/{id}/provenance`: Retrieves complete cryptographic calculation trace.
