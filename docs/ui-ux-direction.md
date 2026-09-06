# ORBIT: UI/UX Direction & Geospatial Workstation Design System

## 1. High-Performance 2D Workstation Paradigm

ORBIT is designed fundamentally as a **High-Performance 2D Geospatial Intelligence Workstation**. The primary viewport prioritizes lightning-fast 2D WebGL rendering, crisp sub-pixel vector road rendering, hardware-accelerated bi-temporal split-screen comparisons, and responsive analytical charting.

```
+-----------------------------------------------------------------------------------+
| CORE INTERFACE: 2D HIGH-PERFORMANCE GEOSPATIAL WORKSTATION (MapLibre GL 2D WebGL) |
| - Instantaneous viewport panning, zooming, and dynamic MVT vector tile streaming   |
| - Hardware-accelerated bi-temporal swipe comparison curtain                       |
| - Sub-pixel vector overlays for change polygons and road network topologies       |
| - Low memory footprint; optimized for local workstation execution                 |
+-----------------------------------------------------------------------------------+
                                         | Modular Optional Layer
                                         v
+-----------------------------------------------------------------------------------+
| FUTURE EXTENSIBILITY: OPTIONAL 3D VISUALIZATION ENGINE (Phase 24+)                |
| - Optional 3D terrain & Copernicus DEM mesh extrusion                             |
| - Optional 3D building LOD2 extrusions where OpenStreetMap data permits           |
| - Optional planetary globe projection (MapLibre Globe / Cesium integration)        |
| * Architectural Invariant: 3D is strictly an optional visual mode, not a core     |
|   dependency for initial intelligence and analytical workflows.                   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Technical Color System (Tactical Dark & Scientific Light)

The design system uses an Earth-inspired, mission-critical color palette that maps directly to semantic physical states:

### Tactical Dark Mode (Default for Low-Light GEOINT Operations):
- **Base Canvas**: `#0B0E14` (Deep Charcoal Void)
- **Substrate / Panels**: `#121824` (Carbon Substrate)
- **Elevated Surfaces / Borders**: `#1E293B` (Slate Matrix) / Border: `#334155`
- **Vegetation / Biomass Accent**: `#10B981` (Chlorophyll Emerald)
- **Hydrology & Telemetry Accent**: `#0EA5E9` (Cyan Water Blue)
- **Urban & Infrastructure Accent**: `#F59E0B` (Amber Built-Up Gold)
- **Critical Change / Anomaly Accent**: `#EF4444` (Spectral Anomaly Scarlet)
- **Typography Primary / Secondary**: `#F8FAFC` (High-Contrast White) / `#94A3B8` (Muted Slate)

### Scientific Light Mode:
- **Base Canvas**: `#F8FAFC` (Cartographic Paper)
- **Panels & Cards**: `#FFFFFF` (Pure Card White)
- **Borders & Dividers**: `#E2E8F0` (Stone Grey)
- **Vegetation Accent**: `#059669` (Deep Forest Green)
- **Hydrology Accent**: `#0284C7` (Cerulean Ocean)
- **Urban Accent**: `#D97706` (Amber Ochre)
- **Anomaly Accent**: `#DC2626` (Crimson Alert)
- **Typography Primary / Secondary**: `#0F172A` (Deep Slate Ink) / `#64748B` (Muted Grey)

---

## 3. Workstation Layout & Component Architecture

The interface is structured into **5 integrated operational zones**:

```
+---------------------------------------------------------------------------------------------------+
| TOP BAR: Global Geocoder | Project Workspace | Telemetry Link Status | Evidence Strength Badge    |
+-------------------+-------------------------------------------------------+-----------------------+
| LEFT DOCK:        | CENTRAL 2D WORKSTATION CANVAS:                        | RIGHT DOCK:           |
|                   |                                                       |                       |
| - Layer Manager   | - MapLibre GL 2D High-Performance Viewport            | - Evidence Inspector  |
| - Optical/SAR     | - Bi-Temporal Split-Screen Swipe Curtain              | - AI Briefing Drawer  |
|   Modality Picker | - Vector Change Mask & Polygon Inspection             | - Authoritative       |
| - Road Hierarchy  | - Geodesic AOI Measurement Tool                       |   Measurement Table   |
| - STAC Catalog    | - Dynamic MVT Road Vector Overlay (5 LoD Zoom Levels) | - Quality Limitations |
+-------------------+-------------------------------------------------------+-----------------------+
| BOTTOM DOCK: Historical Multi-Decadal Timeline (1972-2026) | Epoch Indicators | Annual Event Cards |
+---------------------------------------------------------------------------------------------------+
```

### Key Interactive Components:
1. **Hardware-Accelerated Split-Screen Swipe**: Smooth WebGL curtain comparing baseline vs. target acquisitions.
2. **Interactive Multi-Decadal Timeline**: Displays historical satellite passes, sensor epoch badges (`STRONGLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `ESTIMATED`, `UNAVAILABLE`), and annual metric sparks.
3. **Evidence Strength Inspector**: Dedicated panel displaying calculated $ESI$ score, sensor scene checksums, and processing lineage.
4. **Epistemic Label Badges**: Distinct badges rendering `[OBSERVED]`, `[CALCULATED]`, `[DETECTED]`, `[ESTIMATED]`, `[PREDICTED]`, or `[AI_INTERPRETATION]`.
