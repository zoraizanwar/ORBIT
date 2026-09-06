# ORBIT Architecture: Domain-Driven Design (DDD) & Object Model

## 1. Domain Aggregates & Entity Relationships

ORBIT enforces strict Domain-Driven Design boundaries across its core aggregates:

```mermaid
classDiagram
    class Project {
        +UUID id
        +UUID userId
        +String name
        +String description
        +DateTime createdAt
        +createAOI()
        +listAnalyses()
    }

    class AreaOfInterest {
        +UUID id
        +UUID projectId
        +String name
        +Polygon geometry
        +Polygon boundingBox
        +Float surfaceAreaKm2
        +validateGeometry()
        +computeCentroid()
    }

    class DatasetRegistry {
        +String id
        +String name
        +String providerName
        +SensingModality modality
        +String licenseType
        +String attributionText
        +String commercialTerms
    }

    class ImageryScene {
        +UUID id
        +String datasetId
        +String sceneIdentifier
        +SensingModality modality
        +DateTime acquisitionDatetime
        +Float cloudCoverPercent
        +Float spatialResolutionMeters
        +Polygon geometry
        +Map bandAssets
    }

    class AnalysisRun {
        +UUID id
        +UUID aoiId
        +ExecutionStatus status
        +Int progressPercent
        +AlgorithmTier algorithmTier
        +Map parameters
        +DateTime startedAt
        +DateTime completedAt
        +transitionState(newStatus)
    }

    class Measurement {
        +UUID id
        +UUID analysisRunId
        +String metricName
        +Float value
        +String unit
        +EpistemicLevel epistemicLevel
        +EvidenceStrength evidenceStrength
        +Float uncertaintyMargin
        +Float confidence
    }

    class GeographicEvent {
        +UUID id
        +UUID aoiId
        +String eventTitle
        +String eventCategory
        +Date firstObserved
        +Date lastObserved
        +String lifecycleState
        +MultiPolygon geometry
        +Float affectedAreaKm2
        +EvidenceStrength evidenceStrength
    }

    class EvidenceRecord {
        +UUID id
        +UUID analysisRunId
        +String claimText
        +EpistemicLevel epistemicLevel
        +EvidenceStrength evidenceStrength
        +Float evidenceStrengthScore
        +String sourceTelemetryId
        +String sha256Checksum
    }

    Project "1" *-- "0..*" AreaOfInterest : contains
    AreaOfInterest "1" *-- "0..*" AnalysisRun : executes
    AnalysisRun "1" *-- "0..*" Measurement : produces
    AreaOfInterest "1" *-- "0..*" GeographicEvent : tracks
    AnalysisRun "1" *-- "0..*" EvidenceRecord : justifies
    DatasetRegistry "1" *-- "0..*" ImageryScene : registers
    ImageryScene "1..*" --o "1" AnalysisRun : inputs
```

---

## 2. Value Objects & Value Types

1. **`EvidenceStrength`**:
   - Categorical Value Object (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`) determined deterministically via the $ESI$ composite formula.
2. **`SensingModality`**:
   - Value Type (`OPTICAL_MULTISPECTRAL`, `SAR_MICROWAVE`, `HYBRID_FUSION`) defining sensory physics.
3. **`HistoricalEpoch`**:
   - Value Object bundling temporal bounds, sensor capabilities, and support classifications (`STRONGLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `ESTIMATED`, `UNAVAILABLE`).
4. **`GeodesicArea`**:
   - Immutable spatial scalar calculated via PostGIS `ST_Area(geom::geography)`.
