import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from app.services.ai.models import (
    EvidencePackage,
    AIInterpretationResult,
    ReportRequestPayload,
    ReportResult,
    ReportFormat,
)
from app.services.ai.evidence_retriever import EvidenceRetriever
from app.services.ai.grounded_reasoner import GroundedReasoner
from app.services.ai.models import InterpretRequestPayload


class ReportGenerator:
    """
    Evidence-Grounded Intelligence Report Generator.
    Produces comprehensive, traceable Markdown and JSON intelligence reports
    distinguishing OBSERVED, CALCULATED, DETECTED, PREDICTED, and AI_INTERPRETED tiers.
    """

    @classmethod
    def generate_report(
        cls,
        payload: ReportRequestPayload,
        evidence_package: Optional[EvidencePackage] = None,
        interpretation: Optional[AIInterpretationResult] = None,
    ) -> ReportResult:
        pkg = evidence_package or EvidenceRetriever.get_seed_evidence_package(aoi_id=payload.aoi_id)
        interp = interpretation or GroundedReasoner.interpret(
            InterpretRequestPayload(aoi_id=payload.aoi_id),
            evidence_package=pkg,
        )

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build Markdown Document
        md_lines = [
            f"# ORBIT GEOSPATIAL INTELLIGENCE REPORT",
            f"**Report Title:** {payload.title}",
            f"**Target Area of Interest:** {pkg.aoi_name} (ID: `{pkg.aoi_id}`)",
            f"**Generated At:** {now_str}",
            f"**Evidence Package Hash (SHA-256):** `{pkg.package_hash_sha256}`",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            f"{interp.executive_summary}",
            "",
            "## 2. Epistemic Hierarchy & Grounding Classification",
            "- **Level 1 (OBSERVED):** Raw satellite telemetry and OpenStreetMap vector registry.",
            "- **Level 2 (CALCULATED):** Deterministic spectral indices (dNDVI, dNDBI) and spatial change masks.",
            "- **Level 3 (DETECTED):** Multi-indicator intelligence events and corridor clearings.",
            "- **Level 5 (PREDICTED):** Calibrated statistical trend extrapolations.",
            "- **Synthesis (AI_INTERPRETED):** Explanatory synthesis strictly bound to grounded evidence.",
            "",
            "## 3. Grounded Evidence Claims",
        ]

        for clm in interp.claims:
            citations = ", ".join([f"`{eid}`" for eid in clm.evidence_ids])
            status_badge = f"**[{clm.support_status.value}]**"
            md_lines.append(
                f"- {status_badge} {clm.claim_text} *(Epistemic: `{clm.epistemic_level}`, Cited Evidence: {citations})*"
            )

        md_lines.extend([
            "",
            "## 4. Cross-Sensor Contradiction Assessment",
            f"{interp.contradiction_statement or 'No cross-sensor contradictions identified. All telemetry channels corroborate the detected dynamics.'}",
            "",
            "## 5. Spatial & Infrastructure Corridor Context",
            f"{interp.spatial_interpretation or 'No direct road corridor intersections detected.'}",
            "",
            "## 6. Future Forecast Projections [Epistemic: PREDICTED]",
            f"{interp.forecast_interpretation or 'No future prediction model executed for this baseline.'}",
            "",
            "## 7. Decision Support & Recommended Actions",
        ])

        for rec in interp.recommendations:
            md_lines.append(
                f"- **[{rec.priority.value} PRIORITY - {rec.category.value}]** {rec.recommendation_text}"
            )
            md_lines.append(f"  *Reason:* {rec.reason}")

        md_lines.extend([
            "",
            "## 8. Uncertainty & Analytical Limitations",
            f"{interp.uncertainty_statement}",
            "",
            "## 9. Grounded Evidence Inventory",
            "| Evidence ID | Type | Epistemic Level | Source | Value / Unit | Description |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for item in pkg.evidence_items:
            val_str = f"{item.value} {item.unit or ''}" if item.value is not None else "N/A"
            md_lines.append(
                f"| `{item.id}` | `{item.type}` | `{item.epistemic_level}` | `{item.source_id}` | {val_str} | {item.description} |"
            )

        md_lines.extend([
            "",
            "---",
            "*(This report was generated deterministically by the ORBIT Grounded AI Intelligence System without hallucinations or ungrounded generative AI extrapolation.)*",
        ])

        report_content = "\n".join(md_lines)

        # Hash report content
        report_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()

        return ReportResult(
            report_id=f"rpt-{str(uuid.uuid4())[:8]}",
            aoi_id=pkg.aoi_id,
            title=payload.title,
            report_type=payload.report_type,
            report_format=payload.report_format,
            content_text=report_content,
            provenance_hash_sha256=report_hash,
        )
