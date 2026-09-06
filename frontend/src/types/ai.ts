import { EpistemicLevel, EvidenceStrength } from './index';

export type ClaimType =
  | 'OBSERVATION'
  | 'MEASUREMENT'
  | 'CHANGE'
  | 'CORRELATION'
  | 'FORECAST'
  | 'INTERPRETATION'
  | 'UNCERTAINTY'
  | 'RECOMMENDATION';

export type SupportStatus =
  | 'SUPPORTED'
  | 'PARTIALLY_SUPPORTED'
  | 'UNSUPPORTED'
  | 'CONTRADICTED';

export type RecommendationCategory =
  | 'MONITOR'
  | 'INVESTIGATE'
  | 'COLLECT_MORE_DATA'
  | 'REVIEW_CONTRADICTION'
  | 'PRIORITIZE_SURVEY'
  | 'REASSESS_AFTER_NEW_OBSERVATION';

export type RecommendationPriority = 'HIGH' | 'MEDIUM' | 'LOW';

export type ReportFormat = 'JSON' | 'MARKDOWN' | 'PDF';

export interface EvidenceItem {
  id: string;
  type: string;
  epistemic_level: EpistemicLevel;
  source_id: string;
  source_type: string;
  value?: number;
  unit?: string;
  timestamp?: string;
  geometry_reference?: string;
  quality_score: number;
  evidence_strength: EvidenceStrength;
  description: string;
  provenance: Record<string, any>;
}

export interface EvidenceRelationshipItem {
  id: string;
  source_id: string;
  target_id: string;
  relationship_type: string;
  weight: number;
  description?: string;
}

export interface EvidencePackage {
  package_id: string;
  aoi_id: string;
  aoi_name: string;
  analysis_run_id?: string;
  date_range_start?: string;
  date_range_end?: string;
  evidence_items: EvidenceItem[];
  relationships: EvidenceRelationshipItem[];
  has_contradictions: boolean;
  contradiction_count: number;
  package_hash_sha256: string;
  created_at: string;
}

export interface Claim {
  claim_id: string;
  claim_text: string;
  claim_type: ClaimType;
  epistemic_level: string;
  evidence_ids: string[];
  support_status: SupportStatus;
  confidence: number;
  validation_details: Record<string, any>;
}

export interface Recommendation {
  recommendation_id: string;
  category: RecommendationCategory;
  recommendation_text: string;
  reason: string;
  priority: RecommendationPriority;
  supporting_evidence_ids: string[];
  uncertainty_note?: string;
}

export interface AIInterpretationResult {
  id: string;
  aoi_id: string;
  analysis_run_id?: string;
  intelligence_event_id?: string;
  title: string;
  interpretation_type: string;
  executive_summary: string;
  claims: Claim[];
  recommendations: Recommendation[];
  uncertainty_statement: string;
  contradiction_statement?: string;
  temporal_interpretation?: string;
  spatial_interpretation?: string;
  forecast_interpretation?: string;
  evidence_package_hash: string;
  provider_info: Record<string, any>;
  provenance: Record<string, any>;
  epistemic_level: string;
  created_at: string;
}

export interface ReportResult {
  report_id: string;
  aoi_id: string;
  title: string;
  report_type: string;
  report_format: ReportFormat;
  content_text: string;
  content_pdf_base64?: string;
  provenance_hash_sha256: string;
  created_at: string;
}
