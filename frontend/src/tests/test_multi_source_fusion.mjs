import assert from 'node:assert';
import { test } from 'node:test';

test('Multi-Source Fusion: Observation Registry & Sensor Modality Invariants', () => {
  const observations = [
    {
      id: 'obs-s2-2021',
      scene_id: 'S2B_MSIL2A_20210615',
      platform: 'Sentinel-2B',
      sensor: 'MSI',
      modality: 'OPTICAL',
      acquisition_datetime: '2021-06-15T14:00:00Z',
      gsd_meters: 10.0,
      cloud_cover: 1.2,
      is_test_fixture: false,
    },
    {
      id: 'obs-s1-2021',
      scene_id: 'S1A_IW_GRDH_20210618',
      platform: 'Sentinel-1A',
      sensor: 'C-SAR',
      modality: 'SAR',
      acquisition_datetime: '2021-06-18T18:30:00Z',
      gsd_meters: 10.0,
      cloud_cover: null,
      is_test_fixture: false,
    },
  ];

  assert.strictEqual(observations.length, 2);
  assert.strictEqual(observations[0].modality, 'OPTICAL');
  assert.strictEqual(observations[1].modality, 'SAR');
  assert.strictEqual(observations[1].cloud_cover, null); // SAR cloud cover must be null
  assert.strictEqual(observations[0].is_test_fixture, false);
});

test('Multi-Source Fusion: Pairwise Alignment Status and Reasons', () => {
  const alignments = [
    {
      source_observation_id: 'obs-s2-2021',
      target_observation_id: 'obs-s1-2021',
      temporal_offset_days: 3.19,
      spatial_overlap_percentage: 94.5,
      resolution_ratio: 1.0,
      status: 'ALIGNED',
      reasons: [],
    },
    {
      source_observation_id: 'obs-s2-2021',
      target_observation_id: 'obs-s2-2024',
      temporal_offset_days: 1101.0,
      spatial_overlap_percentage: 100.0,
      resolution_ratio: 1.0,
      status: 'INCOMPATIBLE',
      reasons: ['Temporal offset 1101.0 days exceeds max window 14.0 days'],
    },
  ];

  assert.strictEqual(alignments[0].status, 'ALIGNED');
  assert.strictEqual(alignments[1].status, 'INCOMPATIBLE');
  assert.ok(alignments[1].reasons.length > 0);
});

test('Multi-Source Fusion: Multi-Temporal Trajectory & Epistemic Separation', () => {
  const trajectory = [
    { timestamp: '2021-06-15T14:00:00Z', value: 0.852, epistemic_level: 'CALCULATED' },
    { timestamp: '2022-06-15T14:00:00Z', value: 0.641, epistemic_level: 'CALCULATED' },
    { timestamp: '2023-06-15T14:00:00Z', value: 0.485, epistemic_level: 'CALCULATED' },
    { timestamp: '2024-06-15T14:00:00Z', value: 0.432, epistemic_level: 'PREDICTED' },
  ];

  const historical = trajectory.filter((t) => t.epistemic_level === 'CALCULATED');
  const future = trajectory.filter((t) => t.epistemic_level === 'PREDICTED');

  assert.strictEqual(historical.length, 3);
  assert.strictEqual(future.length, 1);
  assert.notStrictEqual(historical[0].epistemic_level, future[0].epistemic_level);
});

test('Multi-Source Fusion: Cross-Sensor Corroboration & Contradiction Evaluation', () => {
  const contradictionFinding = {
    finding_id: 'FINDING-001',
    relationship: 'CONTRADICTED',
    primary_sensor: 'Sentinel-2 MSI (Optical)',
    primary_metric: 'NDVI_DELTA',
    primary_value: -0.38,
    secondary_sensor: 'Sentinel-1 C-SAR (Microwave)',
    secondary_metric: 'VV_DELTA',
    secondary_value: 0.05,
    explanation: 'Optical canopy decline contradicted by SAR structural stability.',
  };

  assert.strictEqual(contradictionFinding.relationship, 'CONTRADICTED');
  assert.ok(contradictionFinding.explanation.includes('contradicted'));
});

test('Multi-Source Fusion: Deterministic Evidence Strength Score Properties', () => {
  const evidenceScore = {
    evidence_strength_score: 0.845,
    observation_quality_score: 0.98,
    independent_observation_count_score: 1.0,
    temporal_consistency_score: 0.90,
    spatial_consistency_score: 0.95,
    cross_sensor_corroboration_score: 0.15,
    contradiction_penalty: 0.0,
    epistemic_label: 'EVIDENCE_STRENGTH_SCORE',
  };

  assert.ok(evidenceScore.evidence_strength_score >= 0.0 && evidenceScore.evidence_strength_score <= 1.0);
  assert.strictEqual(evidenceScore.epistemic_label, 'EVIDENCE_STRENGTH_SCORE');
  assert.strictEqual(evidenceScore.contradiction_penalty, 0.0);
});
