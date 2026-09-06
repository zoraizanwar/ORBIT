import hashlib
import json
import uuid
from typing import List, Optional
from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.ai.models import (
    EvidenceItem,
    EvidenceRelationshipItem,
    EvidencePackage,
)


class EvidenceRetriever:
    """
    Deterministic Evidence Retrieval & Packaging Engine.
    Collects raw observations, calculated indices, change events, and future predictions
    into an immutable EvidencePackage tagged with a SHA-256 cryptographic digest.
    """

    @classmethod
    def assemble_package(
        cls,
        aoi_id: str,
        aoi_name: str,
        analysis_run_id: Optional[str] = None,
        evidence_items: Optional[List[EvidenceItem]] = None,
        relationships: Optional[List[EvidenceRelationshipItem]] = None,
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None,
    ) -> EvidencePackage:
        items = evidence_items or []
        rels = relationships or []

        # Check for cross-sensor / contradictory edges
        contradiction_edges = [r for r in rels if r.relationship_type == "CONTRADICTS"]
        has_contradictions = len(contradiction_edges) > 0

        # Deterministic SHA-256 Digest Calculation
        digest_payload = {
            "aoi_id": aoi_id,
            "aoi_name": aoi_name,
            "analysis_run_id": analysis_run_id,
            "items": [
                {
                    "id": item.id,
                    "type": item.type,
                    "epistemic_level": item.epistemic_level.value if hasattr(item.epistemic_level, 'value') else str(item.epistemic_level),
                    "source_id": item.source_id,
                    "value": item.value,
                    "unit": item.unit,
                    "timestamp": item.timestamp,
                }
                for item in sorted(items, key=lambda x: x.id)
            ],
            "relationships": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.relationship_type,
                }
                for r in sorted(rels, key=lambda x: (x.source_id, x.target_id))
            ],
        }

        digest_str = json.dumps(digest_payload, sort_keys=True)
        pkg_hash = hashlib.sha256(digest_str.encode("utf-8")).hexdigest()

        return EvidencePackage(
            package_id=str(uuid.uuid4()),
            aoi_id=aoi_id,
            aoi_name=aoi_name,
            analysis_run_id=analysis_run_id,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            evidence_items=items,
            relationships=rels,
            has_contradictions=has_contradictions,
            contradiction_count=len(contradiction_edges),
            package_hash_sha256=pkg_hash,
        )

    @classmethod
    def get_seed_evidence_package(
        cls,
        aoi_id: str = "aoi-sinop-mato-grosso",
        aoi_name: str = "Sinop Deforestation Frontier (Mato Grosso)",
        include_contradiction: bool = False,
    ) -> EvidencePackage:
        """
        Grounded seed evidence package for local testing and deterministic validation.
        """
        items: List[EvidenceItem] = [
            EvidenceItem(
                id="ev-scene-t1",
                type="SCENE",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="S2A_MSIL2A_20230715T135121",
                source_type="Sentinel-2 L2A",
                timestamp="2023-07-15T00:00:00Z",
                quality_score=0.98,
                evidence_strength=EvidenceStrength.STRONG,
                description="Optical multispectral scene acquisition (Cloud Cover: 1.2%)",
            ),
            EvidenceItem(
                id="ev-scene-t2",
                type="SCENE",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="S2A_MSIL2A_20260718T135121",
                source_type="Sentinel-2 L2A",
                timestamp="2026-07-18T00:00:00Z",
                quality_score=0.99,
                evidence_strength=EvidenceStrength.STRONG,
                description="Optical multispectral scene acquisition (Cloud Cover: 0.8%)",
            ),
            EvidenceItem(
                id="ev-ndvi-delta",
                type="INDEX_MEASUREMENT",
                epistemic_level=EpistemicLevel.CALCULATED,
                source_id="dNDVI_Sinop_Sector_A",
                source_type="Spectral Delta Calculation",
                value=-0.24,
                unit="index_delta",
                timestamp="2026-07-18T00:00:00Z",
                quality_score=0.96,
                evidence_strength=EvidenceStrength.STRONG,
                description="Canopy vegetation deficit (dNDVI = -0.24)",
            ),
            EvidenceItem(
                id="ev-ndbi-delta",
                type="INDEX_MEASUREMENT",
                epistemic_level=EpistemicLevel.CALCULATED,
                source_id="dNDBI_Sinop_Sector_A",
                source_type="Spectral Delta Calculation",
                value=0.18,
                unit="index_delta",
                timestamp="2026-07-18T00:00:00Z",
                quality_score=0.95,
                evidence_strength=EvidenceStrength.STRONG,
                description="Impervious surface / built-up expansion (dNDBI = +0.18)",
            ),
            EvidenceItem(
                id="ev-road-corridor",
                type="ROAD_CORRIDOR",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="OSM_Way_BR163",
                source_type="OpenStreetMap Vector Registry",
                value=85.0,
                unit="meters",
                quality_score=1.0,
                evidence_strength=EvidenceStrength.STRONG,
                description="Highway BR-163 primary road corridor (85m proximity)",
            ),
            EvidenceItem(
                id="ev-change-mask",
                type="CHANGE_MASK",
                epistemic_level=EpistemicLevel.CALCULATED,
                source_id="mask_sinop_2023_2026",
                source_type="Spatial Difference Engine",
                value=6.85,
                unit="km2",
                quality_score=0.97,
                evidence_strength=EvidenceStrength.STRONG,
                description="Contiguous vegetation clearance area: 6.85 km²",
            ),
            EvidenceItem(
                id="ev-forecast-2030",
                type="FORECAST_PROJECTION",
                epistemic_level=EpistemicLevel.PREDICTED,
                source_id="fc-run-sinop-lt-v1",
                source_type="Linear Trend Model (ORBIT-LT-v1)",
                value=0.528,
                unit="index_value",
                timestamp="2030-07-01T00:00:00Z",
                quality_score=0.90,
                evidence_strength=EvidenceStrength.MODERATE,
                description="Projected NDVI in 2030 (95% CI: 0.479 – 0.577)",
            ),
        ]

        relationships: List[EvidenceRelationshipItem] = [
            EvidenceRelationshipItem(
                source_id="ev-scene-t1",
                target_id="ev-ndvi-delta",
                relationship_type="DERIVED_FROM",
                weight=1.0,
            ),
            EvidenceRelationshipItem(
                source_id="ev-scene-t2",
                target_id="ev-ndvi-delta",
                relationship_type="DERIVED_FROM",
                weight=1.0,
            ),
            EvidenceRelationshipItem(
                source_id="ev-ndvi-delta",
                target_id="ev-change-mask",
                relationship_type="SUPPORTS",
                weight=1.0,
            ),
            EvidenceRelationshipItem(
                source_id="ev-ndbi-delta",
                target_id="ev-change-mask",
                relationship_type="CORROBORATES",
                weight=1.0,
            ),
            EvidenceRelationshipItem(
                source_id="ev-road-corridor",
                target_id="ev-change-mask",
                relationship_type="LOCATED_IN",
                weight=0.9,
            ),
        ]

        if include_contradiction:
            sar_item = EvidenceItem(
                id="ev-sar-stable",
                type="RADAR_MEASUREMENT",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="S1A_IW_GRDH_20260715",
                source_type="Sentinel-1 SAR C-Band",
                value=0.01,
                unit="dB_delta",
                timestamp="2026-07-15T00:00:00Z",
                evidence_strength=EvidenceStrength.MODERATE,
                description="SAR VH backscatter invariant (+0.01 dB, no radar structural change)",
            )
            items.append(sar_item)
            relationships.append(
                EvidenceRelationshipItem(
                    source_id="ev-sar-stable",
                    target_id="ev-ndvi-delta",
                    relationship_type="CONTRADICTS",
                    weight=1.0,
                    description="Optical canopy deficit is contradicted by stable radar backscatter amplitude",
                )
            )

        return cls.assemble_package(
            aoi_id=aoi_id,
            aoi_name=aoi_name,
            analysis_run_id="run-demo-001",
            evidence_items=items,
            relationships=relationships,
            date_range_start="2023-07-15T00:00:00Z",
            date_range_end="2026-07-18T00:00:00Z",
        )
