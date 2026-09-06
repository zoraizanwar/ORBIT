# ORBIT: Historical Intelligence & Multi-Decadal Capability Model

## 1. Multi-Decadal Historical Capability Model (1972–Present)

ORBIT treats historical Earth Observation telemetry as heterogeneous across time. The analytical capabilities, spatial resolutions, and temporal frequencies of 1972 are fundamentally different from 2026. The platform models historical intelligence through **4 Sensor Epochs**:

```
+----------------------------------------------------------------------------------------------------+
| EPOCH 1: 1972–1981 (Landsat 1–3 MSS Pioneer Era)                                                   |
| - Spatial Resolution: 60m x 80m | Spectral: 4 Broad Optical Bands | Cadence: 18 Days               |
| - Capability: Macro-scale land-water boundaries, major continental deforestation, reservoir creation|
| - Support Level: `LIMITED` / `ESTIMATED`. Fine urban and road analysis: `UNAVAILABLE`.             |
+----------------------------------------------------------------------------------------------------+
                                                 ↓
+----------------------------------------------------------------------------------------------------+
| EPOCH 2: 1982–1998 (Landsat 4–5 Thematic Mapper Multispectral Era)                                 |
| - Spatial Resolution: 30m Optical, 120m Thermal | Spectral: 7 Bands (Visible, NIR, SWIR, TIR)     |
| - Capability: Regional vegetation indices (NDVI), urban footprint expansion, wetland loss          |
| - Support Level: `MODERATE` to `PARTIALLY_SUPPORTED`. Sub-hectare infrastructure: `UNAVAILABLE`.   |
+----------------------------------------------------------------------------------------------------+
                                                 ↓
+----------------------------------------------------------------------------------------------------+
| EPOCH 3: 1999–2014 (Landsat 7 ETM+ & MODIS Era)                                                    |
| - Spatial Resolution: 30m Multispectral, 15m Panchromatic | Cadence: 16 Days (SLC-off post-2003)   |
| - Capability: Enhanced regional change tracking; SLC-off gap masking/interpolation required        |
| - Support Level: `MODERATE`. Moderate urban corridor detection supported.                         |
+----------------------------------------------------------------------------------------------------+
                                                 ↓
+----------------------------------------------------------------------------------------------------+
| EPOCH 4: 2015–PRESENT (Sentinel-1/2 & Landsat 8/9 High-Resolution Multi-Modal Constellation Era)  |
| - Spatial Resolution: 10m-20m MSI, 10m C-Band SAR | Cadence: 5 Days (Constellation revisit)       |
| - Capability: High-precision bi-temporal change, road paving, discrete event tracking, SAR fusion|
| - Support Level: `STRONGLY_SUPPORTED`. Full Level 1-4 analytical pipeline active.                  |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Annual Summary Support Classifications

For any requested year in a multi-decadal timeline, the Historical Intelligence Engine assigns an explicit **Annual Support Classification**:

| Support Level Badge | Criteria & Data Availability | System Behavior & Output |
|---|---|---|
| **`STRONGLY_SUPPORTED`** | $\ge 4$ cloud-free ($< 10\%$) high-resolution ($10\text{m}-20\text{m}$) acquisitions within target year; multi-spectral & SAR coverage available. | Full annual intelligence vector computed; all index means, land-cover changes, and discrete events generated. |
| **`PARTIALLY_SUPPORTED`** | $1 - 3$ cloud-free standard-resolution ($30\text{m}$) acquisitions (Landsat 4-7); seasonal baseline available. | Annual index averages computed with documented confidence bounds; fine road/urban events marked as unobservable. |
| **`ESTIMATED`** | Cloud-contaminated observations ($> 20\%$) requiring temporal harmonic interpolation (CCDC) or coarse MODIS telemetry. | Trend metrics estimated with explicit $\pm$ variance bounds; clear `[ESTIMATED]` tag in UI and reports. |
| **`UNAVAILABLE`** | Zero viable telemetry or gap period (e.g. pre-1972, or missing satellite passes). | Engine returns `INSUFFICIENT_EVIDENCE`. **Zero synthetic data is fabricated.** Annual card displays "Insufficient Telemetry Evidence." |

---

## 3. Deep Geological & Archaeological History Module

For multi-millennial inquiries:
- **Geological Epochs**: Quaternary, Neogene, Paleogene stratigraphic boundaries linked to global sea-level curves and paleoclimatic ice-core benchmarks.
- **Paleo-Hydrology**: Ancient river channels and fossil aquifers mapped from radar penetration data.
- **Archaeological Gazettes**: Integration of open peer-reviewed archaeological registries (Pleiades, OpenContext).

---

## 4. Dedicated Islamic Sources Historical Layer

Maintains a rigorous, scholarly-classified **Islamic Sources Engine** adhering to classical Islamic historiographical methodology (*Ilm al-Hadith* and *Usul al-Tarikh*):

### Strict Classification Framework:
- `QURAN`: Verified verses from the Uthmanic codex (Mutawatir Qat'i).
- `MUTAWATIR_HADITH`: Mass-transmitted traditions with unbroken chains.
- `AHAD_SAHIH`: Rigorously authenticated single-chain traditions (Bukhari, Muslim, etc.).
- `SCHOLARLY_IJMA`: Documented geographic consensus of classical geographers (Al-Idrisi, Yaqut al-Hamawi).
- `HISTORICAL_TARIKH`: General Islamic historiographical chronicles (Al-Tabari, Ibn Kathir).
- `UNVERIFIED_ISRAILIYYAT`: Quarantined folklore, explicitly labeled as non-authoritative.

### Invariant Rules:
1. **Zero Fabrication**: No religious claims, itineraries, or narrations are fabricated.
2. **Epistemic Independence**: Scientific empirical dating and religious texts are maintained as separate categories; the system never forces scientific evidence to fit theological traditions nor religious traditions to fit scientific models.
3. **Cosmic Age Invariant**: The system never asserts a specific numerical age of the Earth or cosmos as an "Islamic fact."
