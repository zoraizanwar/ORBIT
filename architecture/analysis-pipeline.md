# ORBIT Architecture: Analysis Pipeline & Worker State Machine

## 1. Analysis Lifecycle State Machine

Analysis runs transition through a deterministic, strictly monitored lifecycle state machine:

```mermaid
stateDiagram-v2
    [*] --> QUEUED : User submits analysis request
    QUEUED --> INGESTING : Celery worker acquires lock & initiates STAC discovery
    
    INGESTING --> PROCESSING : Modality evaluated (Optical vs SAR) & COG windows fetched
    INGESTING --> FAILED : Provider unreachable / No viable scenes
    
    PROCESSING --> ANALYZING : Cloud-masked index rasters (Level 1) computed
    PROCESSING --> FAILED : Raster dimension mismatch / Corrupted COG
    
    ANALYZING --> SYNTHESIZING : Tiered Change Detection (Levels 2-4) & Geodesics executed
    ANALYZING --> FAILED : Zero valid pixels remaining after cloud mask
    
    SYNTHESIZING --> COMPLETED : Level 5 Grounded AI Briefing verified & PDF rendered
    SYNTHESIZING --> FAILED : LLM output validation error / Hallucination detected
    
    QUEUED --> CANCELLED : User aborts request
    INGESTING --> CANCELLED : User aborts request
    PROCESSING --> CANCELLED : User aborts request
    
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

---

## 2. Tiered Change Detection Execution & Worker Topology

Celery workers are partitioned into specialized queues to isolate heavy raster processing from lightweight geocoding and report generation:

```
+-----------------------------------------------------------------------------------+
| QUEUE 1: `celery_fast` (Concurrency: 8 workers)                                   |
| - Location geocoding & gazetteer resolution                                        |
| - STAC catalog search and modality suitability evaluation                         |
| - Dynamic MVT tile generation cache warmups                                       |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
| QUEUE 2: `celery_raster` (Concurrency: 4 workers, High-Memory / NumPy Optimized)   |
| - HTTP Range windowed COG tile reads                                              |
| - Tier 1: Radiometric band math (NDVI, NDWI, NDBI) and SCL cloud masking          |
| - Tier 2: Bi-temporal differencing, Otsu baseline, CCDC harmonic modeling         |
| - Tier 3: Morphological segmentation and object extraction                        |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
| QUEUE 3: `celery_intel` (Concurrency: 4 workers)                                  |
| - Tier 4: PostGIS spatial clustering (ST_ClusterDBSCAN) & geodesic ST_Area        |
| - Evidence Strength ($ESI$) evaluation and cryptographic SHA-256 DAG recording    |
| - Tier 5: Grounded LLM narrative synthesis + Anti-hallucination validation gate   |
| - WeasyPrint / ReportLab PDF compilation and artifact packaging                   |
+-----------------------------------------------------------------------------------+
```
