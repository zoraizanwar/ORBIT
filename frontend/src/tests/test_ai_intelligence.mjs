import { test } from 'node:test';
import assert from 'node:assert/strict';

// Grounded Demo Evidence Package Fixture
const DEMO_EVIDENCE_PACKAGE = {
  package_id: 'pkg-demo-sinop-001',
  aoi_id: 'aoi-sinop-mato-grosso',
  aoi_name: 'Sinop Deforestation Frontier (Mato Grosso)',
  evidence_items: [
    {
      id: 'ev-scene-t1',
      type: 'SCENE',
      epistemic_level: 'OBSERVED',
      source_id: 'S2A_MSIL2A_20230715',
      value: null,
      description: 'Optical multispectral scene acquisition',
    },
    {
      id: 'ev-ndvi-delta',
      type: 'INDEX_MEASUREMENT',
      epistemic_level: 'CALCULATED',
      source_id: 'dNDVI_Sinop',
      value: -0.24,
      unit: 'index_delta',
      description: 'Canopy vegetation deficit (dNDVI = -0.24)',
    },
    {
      id: 'ev-road-corridor',
      type: 'ROAD_CORRIDOR',
      epistemic_level: 'OBSERVED',
      source_id: 'OSM_Way_BR163',
      value: 85.0,
      unit: 'meters',
      description: 'Highway BR-163 primary road corridor',
    },
    {
      id: 'ev-forecast-2030',
      type: 'FORECAST_PROJECTION',
      epistemic_level: 'PREDICTED',
      source_id: 'ORBIT-LT-v1',
      value: 0.528,
      timestamp: '2030-07-01T00:00:00Z',
      description: 'Projected NDVI in 2030',
    },
  ],
  relationships: [
    {
      source_id: 'ev-scene-t1',
      target_id: 'ev-ndvi-delta',
      relationship_type: 'DERIVED_FROM',
    },
  ],
  has_contradictions: false,
  package_hash_sha256: '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e',
};

const DEMO_AI_INTERPRETATION = {
  id: 'ai-interp-sinop-001',
  aoi_id: 'aoi-sinop-mato-grosso',
  epistemic_level: 'AI_INTERPRETED',
  claims: [
    {
      claim_id: 'clm-obs-1',
      claim_text: 'Telemetry observation confirmed from source S2A_MSIL2A_20230715.',
      claim_type: 'OBSERVATION',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-scene-t1'],
      support_status: 'SUPPORTED',
      confidence: 0.98,
    },
    {
      claim_id: 'clm-change-1',
      claim_text: 'Canopy vegetation deficit of -0.24 coincides with road corridor proximity.',
      claim_type: 'CHANGE',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-ndvi-delta', 'ev-road-corridor'],
      support_status: 'SUPPORTED',
      confidence: 0.95,
    },
    {
      claim_id: 'clm-forecast-1',
      claim_text: 'Calibrated model projects metric value to reach 0.528 by 2030.',
      claim_type: 'FORECAST',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-forecast-2030'],
      support_status: 'SUPPORTED',
      confidence: 0.88,
    },
  ],
  recommendations: [
    {
      recommendation_id: 'rec-1',
      category: 'MONITOR',
      recommendation_text: 'Maintain scheduled satellite surveillance pass over active BR-163 perimeter.',
      reason: 'Corridor clearance confirmed with high confidence.',
      priority: 'HIGH',
      supporting_evidence_ids: ['ev-ndvi-delta', 'ev-road-corridor'],
    },
  ],
  evidence_package_hash: '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e',
};

test('Grounded AI: Strict Epistemic Classification Invariant', () => {
  assert.equal(DEMO_AI_INTERPRETATION.epistemic_level, 'AI_INTERPRETED');

  // Verify that all AI claims are tagged AI_INTERPRETED and not raw sensor levels
  for (const claim of DEMO_AI_INTERPRETATION.claims) {
    assert.equal(claim.epistemic_level, 'AI_INTERPRETED');
    assert.notEqual(claim.epistemic_level, 'OBSERVED');
    assert.notEqual(claim.epistemic_level, 'CALCULATED');
    assert.notEqual(claim.epistemic_level, 'PREDICTED');
  }
});

test('Grounded AI: Claim-Level Evidence Citation Invariant', () => {
  const validEvidenceIds = new Set(DEMO_EVIDENCE_PACKAGE.evidence_items.map((i) => i.id));

  for (const claim of DEMO_AI_INTERPRETATION.claims) {
    assert.ok(claim.evidence_ids.length > 0, `Claim ${claim.claim_id} must cite at least one evidence item`);
    for (const eid of claim.evidence_ids) {
      assert.ok(validEvidenceIds.has(eid), `Cited evidence ID ${eid} must exist in the Evidence Package`);
    }
  }
});

test('Grounded AI: Future Prediction Remains Grounded in Model Forecast', () => {
  const forecastClaim = DEMO_AI_INTERPRETATION.claims.find((c) => c.claim_type === 'FORECAST');
  assert.ok(forecastClaim, 'Forecast claim must exist');
  assert.ok(forecastClaim.evidence_ids.includes('ev-forecast-2030'));

  // The evidence referenced must be PREDICTED
  const referencedItem = DEMO_EVIDENCE_PACKAGE.evidence_items.find((i) => i.id === 'ev-forecast-2030');
  assert.equal(referencedItem.epistemic_level, 'PREDICTED');
});

test('Grounded AI: Decision Support Priority and Grounding', () => {
  assert.ok(DEMO_AI_INTERPRETATION.recommendations.length >= 1);
  const rec = DEMO_AI_INTERPRETATION.recommendations[0];
  assert.ok(['HIGH', 'MEDIUM', 'LOW'].includes(rec.priority));
  assert.ok(rec.supporting_evidence_ids.length > 0);
});

test('Grounded AI: Cryptographic Provenance SHA-256 Digest', () => {
  assert.equal(DEMO_AI_INTERPRETATION.evidence_package_hash.length, 64);
  assert.equal(DEMO_EVIDENCE_PACKAGE.package_hash_sha256.length, 64);
  assert.equal(
    DEMO_AI_INTERPRETATION.evidence_package_hash,
    DEMO_EVIDENCE_PACKAGE.package_hash_sha256
  );
});
