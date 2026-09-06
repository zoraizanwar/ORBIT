# ORBIT: Geospatial Architecture & Spatial Computation Engine

## 1. Coordinate Reference Systems (CRS) & Geodetic Standards

Geospatial calculations in ORBIT must maintain rigorous mathematical precision across global extents. The architecture establishes strict rules for coordinate system transformations:

```
+-----------------------------------------------------------------------------------+
| 1. CANONICAL STORAGE & API EXCHANGE: EPSG:4326 (WGS84 Ellipsoidal Lon/Lat)         |
|    - All database geometries (AOIs, Road vectors, Scene footprints, Change masks) |
|    - GeoJSON exchanges between frontend and backend                               |
+-----------------------------------------------------------------------------------+
                                         | Reprojection as required
                                         v
+-----------------------------------------------------------------------------------+
| 2. DETERMINISTIC GEODESIC MEASUREMENTS: WGS84 Ellipsoid (PostGIS Geography)       |
|    - Computations use `ST_Area(geom::geography, use_spheroid=true)`               |
|    - Accurate ellipsoidal distance calculations via Great Circle / Vincenty       |
|    - Elimination of high-latitude planar distortion (e.g. Mercator area error)     |
+-----------------------------------------------------------------------------------+
                                         | Dynamic Projected Windowing
                                         v
+-----------------------------------------------------------------------------------+
| 3. RASTER PIXEL ANALYSIS: Auto-UTM Projection (EPSG:32601 - EPSG:32760)           |
|    - Raster band arrays reprojected to local UTM zone matching AOI centroid       |
|    - Guarantees equidistant, orthogonal grid cells for kernel operations and cv    |
+-----------------------------------------------------------------------------------+
                                         | Tile Rendering
                                         v
+-----------------------------------------------------------------------------------+
| 4. WEB CLIENT RENDERING: EPSG:3857 (Pseudo-Mercator / Spherical Mercator)         |
|    - Dynamic Mapbox Vector Tiles (MVT) generated via `ST_AsMVT`                   |
|    - MapLibre GL raster and vector tile ingestion                                 |
+-----------------------------------------------------------------------------------+
```

---

## 2. Dynamic Vector Tile (MVT) Generation Pipeline

To enable smooth visualization of millions of global mapped roads and spatial change polygons without overloading the client browser, ORBIT implements a server-side dynamic MVT tile endpoint:

$$\text{GET } /\text{api/v1/geo/tiles/roads/}\{z\}/\{x\}/\{y\}\text{.pbf}$$

### Tile SQL Engine Query Pattern
```sql
WITH tile_bounds AS (
    SELECT ST_TileEnvelope(:z, :x, :y) AS bbox
),
filtered_roads AS (
    SELECT 
        r.id,
        r.name,
        r.road_class,
        r.surface,
        r.lanes,
        r.bridge,
        r.tunnel,
        ST_AsMVTGeom(
            ST_Transform(r.geometry, 3857),
            tb.bbox,
            4096, -- Tile resolution extent
            256,  -- Buffer margin to prevent clipping
            true  -- Clip geometry
        ) AS mvt_geom
    FROM geo.road_features r, tile_bounds tb
    WHERE ST_Intersects(r.geometry, ST_Transform(tb.bbox, 4326))
      AND (
          (:z <= 8 AND r.road_class IN ('motorway', 'trunk')) OR
          (:z BETWEEN 9 AND 11 AND r.road_class IN ('motorway', 'trunk', 'primary', 'secondary')) OR
          (:z >= 12)
      )
)
SELECT ST_AsMVT(filtered_roads.*, 'roads', 4096, 'mvt_geom') AS mvt_tile
FROM filtered_roads;
```

---

## 3. Road Network Progressive Detail & Level of Detail (LoD)

To prevent browser memory crashes when viewing continental scales while ensuring sub-meter accuracy when zooming in to city blocks, ORBIT enforces a **5-Tier Level of Detail (LoD) Pyramid**:

| LoD Tier | Zoom Levels | Displayed Road Classes | Simplification Tolerance (Douglas-Peucker) | PostGIS Source Table / Index Target |
|---|---|---|---|---|
| **LoD 0 (Macro)** | $Z = 0 - 5$ | Motorways & Trunk Highways only | $0.05^\circ$ ($\approx 5.5\text{ km}$) | `geo.road_features` where `road_class IN ('motorway')` |
| **LoD 1 (Regional)** | $Z = 6 - 8$ | Motorway, Trunk, Primary corridors | $0.01^\circ$ ($\approx 1.1\text{ km}$) | `geo.road_features` with highway index |
| **LoD 2 (Metro)** | $Z = 9 - 11$ | Primary, Secondary, Tertiary arterial routes | $0.002^\circ$ ($\approx 220\text{ m}$) | `geo.road_features` with highway index |
| **LoD 3 (District)** | $Z = 12 - 14$ | Residential, Unclassified, Collector roads | $0.0005^\circ$ ($\approx 55\text{ m}$) | `geo.road_features` unfiltered |
| **LoD 4 (Street Level)**| $Z \ge 15$ | Service roads, alleys, tracks, bridges, tunnels | No simplification ($0.0\text{ m}$) | `geo.road_features` full fidelity |

---

## 4. Rigorous Geodesic Measurement Mathematics

Planar area calculations ($x \times y$) using latitude/longitude degrees introduce massive geometric errors increasing with latitude:

$$\text{Error}_{\text{Mercator}}(\phi) = \frac{1}{\cos^2(\phi)} - 1$$

At $\phi = 60^\circ$ latitude, standard planar calculations overstate true physical surface area by **300% (4x)**.

### Measurement Invariants in ORBIT:
1. **Surface Area ($km^2$)**:
   $$\text{Area}_{\text{geodesic}} = \text{ST\_Area}(\text{geom}::\text{geography}, \text{use\_spheroid} = \text{true}) \times 10^{-6}$$
2. **Linear Distance / Road Disturbance Length ($km$)**:
   $$\text{Length}_{\text{geodesic}} = \text{ST\_Length}(\text{geom}::\text{geography}, \text{use\_spheroid} = \text{true}) \times 10^{-3}$$
3. **Change Fragmentation Metric**:
   $$\text{Fragmentation Index} = \frac{\text{Perimeter}_{\text{geodesic}}}{2 \sqrt{\pi \cdot \text{Area}_{\text{geodesic}}}}$$
   *(Values near 1.0 indicate compact circular clearings; high values $> 5.0$ denote dendritic infrastructure encroachment).*
