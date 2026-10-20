// ============================================================================
// Rebuild the criterion layers for the Kavrepalanchowk apiary suitability model
// from the original public data, in Google Earth Engine (code.earthengine.google.com).
// Follows the draft's Section 3.2 and Table 2 rules. Every layer is exported on
// ONE grid: EPSG:32645, 10 m cells, origin at (0, 0), same region. 0 = NoData.
//
// OpenStreetMap version. Before running: upload gis_osm_waterways_free_1 and
// gis_osm_roads_free_1 (Geofabrik Nepal) as table assets, and paste their
// Table IDs below. Then press Run, open the Tasks tab and click RUN on each export.
// ============================================================================

// ---------------- 1. Settings: edit these ----------------
var RIVERS_ID = 'projects/YOUR-EE-PROJECT/assets/kavre_rivers';
var ROADS_ID  = 'projects/YOUR-EE-PROJECT/assets/kavre_roads';
var BOUNDARY_ASSET = 'projects/YOUR-EE-PROJECT/assets/kavre_boundary';
var FOLDER = 'apiary_rasters';                                       // Google Drive folder
var USING_OSM = true;    // true if rivers/roads are Geofabrik OpenStreetMap layers (gis_osm_waterways / gis_osm_roads)

if (RIVERS_ID.indexOf('PASTE') === 0 || ROADS_ID.indexOf('PASTE') === 0) {
  throw new Error('Paste your two Table IDs into RIVERS_ID and ROADS_ID at the top of the script first.');
}
var RIVERS = ee.FeatureCollection(RIVERS_ID);
var ROADS = ee.FeatureCollection(ROADS_ID);

var CRS = 'EPSG:32645';
var GRID = [10, 0, 0, 0, -10, 0];          // 10 m cells, origin (0,0): identical grid for every export

// ---------------- 2. District boundary ----------------
// Found by location (the district containing Dhulikhel, Kavre's headquarters). Several boundary
// datasets are tried and the one closest to Kavre's official area (1,396 km2) is used.
var DHULIKHEL = ee.Geometry.Point([85.5461, 27.6195]);
var district, districtFC;
if (BOUNDARY_ASSET) {   // e.g. GADM 4.1 level 3 (all Nepal districts): the one containing Dhulikhel is used
  districtFC = ee.FeatureCollection(BOUNDARY_ASSET).filterBounds(DHULIKHEL);
  var nB = districtFC.size().getInfo();
  if (nB !== 1) {
    throw new Error('The boundary asset has ' + nB + ' polygons at Dhulikhel (expected 1). Upload the district-level file (gadm41_NPL_3).');
  }
  var kmB = districtFC.geometry().area(1).divide(1e6).getInfo();
  if (kmB < 1250 || kmB > 1550) {
    throw new Error('Boundary asset area is ' + kmB.toFixed(0) + ' km2, not Kavre (about 1,396). Check that you uploaded gadm41_NPL_3.');
  }
} else {
  var candidates = [
    ['FAO GAUL 2015 level 2', 'FAO/GAUL/2015/level2'],
    ['geoBoundaries ADM2', 'WM/geoLab/geoBoundaries/600/ADM2'],
    ['FAO GAUL simplified level 2', 'FAO/GAUL_SIMPLIFIED_500m/2015/level2']
  ];
  var best = null, bestErr = 1e9;
  candidates.forEach(function (c) {
    var fc = ee.FeatureCollection(c[1]).filterBounds(DHULIKHEL);
    var n = fc.size().getInfo();
    if (n !== 1) { print(c[0] + ': ' + n + ' features, skipped'); return; }
    var km2 = fc.geometry().area(1).divide(1e6).getInfo();
    print(c[0] + ': ' + km2.toFixed(1) + ' km2');
    if (Math.abs(km2 - 1396) < bestErr) { bestErr = Math.abs(km2 - 1396); best = [c[0], fc]; }
  });
  if (best === null || bestErr > 70) {
    throw new Error('No boundary dataset is within 5% of Kavre (1,396 km2). Upload your own Kavre boundary ' +
      'shapefile as an asset and put its Table ID in BOUNDARY_ASSET.');
  }
  print('Using boundary from: ' + best[0]);
  districtFC = best[1];
}
district = districtFC.geometry();
var areaKm2 = district.area(1).divide(1e6).getInfo();
print('District found:', districtFC.first().toDictionary());
print('District area km2 (official about 1,396):', areaKm2);
Map.centerObject(district, 10);
var region = district.transform(CRS, 1).bounds(1, CRS);

function onGrid(img, method) {   // put any image on the analysis grid
  img = method === 'bilinear' ? img.resample('bilinear') : img;
  return img.reproject({crs: CRS, crsTransform: GRID});
}

// ---------------- 3. LULC (Esri 10 m, 2024) ----------------
var lulcCol = ee.ImageCollection('projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS')
  .filterDate('2024-01-01', '2025-01-01').filterBounds(district);
var lulcRaw = lulcCol.mosaic().select([0], ['lulc']).setDefaultProjection(lulcCol.first().projection());
print('LULC class histogram (should use codes 1,2,4,5,7,8,9,10,11):',
      lulcRaw.reduceRegion({reducer: ee.Reducer.frequencyHistogram(), geometry: district,
                            crs: CRS, crsTransform: GRID, maxPixels: 1e10}));
var LULC = lulcRaw.remap([1, 2, 4, 5, 7, 8, 9, 11], [2, 9, 2, 5, 1, 1, 1, 7]);   // 10 = Clouds -> masked

// ---------------- 4. NDVI (Sentinel-2 L2A, 2019-2023 median) ----------------
function maskS2(img) {
  var scl = img.select('SCL');
  var bad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11)); // shadow, cloud med/high, cirrus, snow
  return img.updateMask(bad.not());
}
var ndviRaw = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(district).filterDate('2019-01-01', '2024-01-01')
  .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 20))
  .map(maskS2)
  .map(function (i) { return i.normalizedDifference(['B8', 'B4']).rename('ndvi'); })
  .median()
  .setDefaultProjection({crs: CRS, scale: 10});   // composites need their native 10 m projection

// ---------------- 5. LST (MOD11A2 V061 daytime, 2020-2024) ----------------
function lstQC(img) {
  var qc = img.select('QC_Day');
  var mandatory = qc.bitwiseAnd(3);                 // bits 0-1
  var err = qc.rightShift(6).bitwiseAnd(3);         // bits 6-7: 0 = <=1 K, 1 = <=2 K
  var keep = mandatory.eq(0).or(mandatory.eq(1).and(err.lte(1)));
  return img.select('LST_Day_1km').updateMask(keep).multiply(0.02).subtract(273.15);
}
var years = ee.List.sequence(2020, 2024);
var lstRaw = ee.ImageCollection(years.map(function (y) {
  y = ee.Number(y);
  return ee.ImageCollection('MODIS/061/MOD11A2')
    .filterDate(ee.Date.fromYMD(y, 1, 1), ee.Date.fromYMD(y.add(1), 1, 1))
    .map(lstQC).mean();
})).mean().rename('lst')
  .setDefaultProjection(ee.ImageCollection('MODIS/061/MOD11A2').first().select('LST_Day_1km').projection());

// NOTE: this CHIRPS layer is used only for the precipitation sensitivity run (data/standardised/PREC_CHIRPS.tif).
// The main PREC layer is WorldClim V1 1960-1990 (gee/04_precip_worldclim.js), scored to 1-9 with scripts/02_prep_layers.py score.
// ---------------- 6. Precipitation (CHIRPS daily, 2020-2024 mean annual total) ----------------
var precRaw = ee.ImageCollection(years.map(function (y) {
  y = ee.Number(y);
  return ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterDate(ee.Date.fromYMD(y, 1, 1), ee.Date.fromYMD(y.add(1), 1, 1)).sum();
})).mean().rename('prec')
  .setDefaultProjection(ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').first().projection());

// ---------------- 7. Terrain (Copernicus GLO-30) ----------------
var demCol = ee.ImageCollection('COPERNICUS/DEM/GLO30').filterBounds(district).select('DEM');
var dem = demCol.mosaic().setDefaultProjection(demCol.first().projection())
  .reproject({crs: CRS, scale: 30}).rename('elev');
var slopeDeg = ee.Terrain.slope(dem);
var aspectDeg = ee.Terrain.aspect(dem);
var flat = slopeDeg.lt(0.001);
var a = aspectDeg;
var ASPECT30 = ee.Image(5)                                            // north-facing default
  .where(a.gte(22.5).and(a.lt(67.5)).or(a.gt(292.5).and(a.lte(337.5))), 6)
  .where(a.gte(67.5).and(a.lt(112.5)).or(a.gt(247.5).and(a.lte(292.5))), 7)
  .where(a.gte(112.5).and(a.lt(157.5)).or(a.gt(202.5).and(a.lte(247.5))), 8)
  .where(a.gte(157.5).and(a.lte(202.5)), 9)
  .where(flat, 4)
  .updateMask(dem.mask());

// ---------------- 8. Distances to rivers and roads (100 m bands) ----------------
function distScore(fc) {
  var lines = ee.Image(0).byte().paint(fc, 1).selfMask();
  var d = onGrid(lines, 'nearest').unmask(0)
    .fastDistanceTransform(128, 'pixels', 'squared_euclidean').sqrt().multiply(10)
    .unmask(1e6);  // metres; anything beyond 1.28 km scores 1 anyway
  return ee.Image(9).subtract(d.divide(100).floor()).max(1).rename('score');
}
if (USING_OSM) {   // match the draft's definitions: natural watercourses only; vehicular roads only
  RIVERS = RIVERS.filter(ee.Filter.inList('fclass', ['river', 'stream']));
  ROADS = ROADS.filter(ee.Filter.inList('fclass',
    ['footway', 'path', 'steps', 'pedestrian', 'bridleway', 'cycleway', 'unknown']).not());
}
RIVERS = RIVERS.filterBounds(district.buffer(2000));
ROADS = ROADS.filterBounds(district.buffer(2000));
ee.List([RIVERS.size(), ROADS.size()]).evaluate(function (n) {
  if (!n) { return; }
  print('Features inside the district (plus 2 km): rivers ' + n[0] + ', roads ' + n[1]);
  if (n[0] === 0 || n[1] === 0) { print('WARNING: no rivers or roads inside the district. Do not export; check the asset IDs.'); }
});
var WATER = distScore(RIVERS);
var ROAD = distScore(ROADS);

// ---------------- 9. Align and build the common mask ----------------
var elevG = onGrid(dem, 'bilinear');
var slopeG = onGrid(slopeDeg, 'bilinear');
var ndviG = onGrid(ndviRaw, 'bilinear');
var lstG = onGrid(lstRaw, 'bilinear');
var precG = onGrid(precRaw, 'bilinear');
var lulcG = onGrid(LULC, 'nearest');
var aspectG = onGrid(ASPECT30, 'nearest');
var waterG = onGrid(WATER, 'nearest');
var roadG = onGrid(ROAD, 'nearest');

var inside = ee.Image(1).clip(district);
var mask = inside.updateMask(lulcG.mask()).updateMask(ndviG.mask()).updateMask(lstG.mask())
  .updateMask(precG.mask()).updateMask(elevG.mask()).updateMask(slopeG.mask())
  .updateMask(aspectG.mask()).mask().gt(0);

// ---------------- 10. Standardise to 1-9 (Table 2) ----------------
var ELEV = ee.Image(1)
  .where(elevG.gte(200).and(elevG.lt(400)), 2).where(elevG.gte(400).and(elevG.lt(600)), 3)
  .where(elevG.gte(600).and(elevG.lt(800)), 5).where(elevG.gte(800).and(elevG.lt(1000)), 7)
  .where(elevG.gte(1000).and(elevG.lte(1500)), 9).where(elevG.gt(1500).and(elevG.lte(2000)), 8)
  .where(elevG.gt(2000).and(elevG.lte(2500)), 6).where(elevG.gt(2500), 4);
var SLOPE = ee.Image(1)
  .where(slopeG.lte(55), 2).where(slopeG.lte(40), 3).where(slopeG.lte(30), 4).where(slopeG.lte(25), 5)
  .where(slopeG.lte(20), 6).where(slopeG.lte(15), 7).where(slopeG.lte(10), 8).where(slopeG.lte(5), 9);

function nineIntervals(img, name) {   // nine equal intervals over the observed range inside the mask
  var mm = img.updateMask(mask).reduceRegion({reducer: ee.Reducer.minMax(), geometry: district,
    crs: CRS, crsTransform: GRID, maxPixels: 1e10});
  var vals = mm.values().sort();
  var lo = ee.Number(vals.get(0)), hi = ee.Number(vals.get(1));
  vals.evaluate(function (v, err) {   // runs in the background so the page stays responsive
    if (err) { print(name + ' range check could not finish in the Console (exports are unaffected): ' + err); return; }
    if (!v || v[0] === null || v[1] - v[0] < 1e-6) {
      print('WARNING: ' + name + ' has no spread inside the district (' + v + '). Do not export; send a screenshot.');
    } else {
      print(name + ' observed range inside mask (for Table 2): ' + v[0] + ' to ' + v[1]);
    }
  });
  var step = hi.subtract(lo).divide(9);
  return img.subtract(lo).divide(step).floor().add(1).min(9).max(1);
}
var NDVI = nineIntervals(ndviG, 'NDVI');
var LST = nineIntervals(lstG, 'LST (degC)');
var PREC = nineIntervals(precG, 'Precipitation (mm/yr)');

// ---------------- 11. Export (Byte, 0 = NoData) ----------------
function exp(img, name) {
  Export.image.toDrive({image: img.updateMask(mask).unmask(0).toByte().clip(district),
    description: name, folder: FOLDER, fileNamePrefix: name, region: region,
    crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});
}
exp(lulcG, 'LULC');
exp(NDVI, 'NDVI'); exp(LST, 'LST'); exp(PREC, 'PREC');
exp(ELEV, 'ELEV'); exp(SLOPE, 'SLOPE'); exp(aspectG, 'ASPECT');
exp(waterG, 'WATER'); exp(roadG, 'ROAD');

// Raw continuous surfaces (float, for reporting ranges and checks)
function expRaw(img, name) {
  Export.image.toDrive({image: img.updateMask(mask).toFloat().clip(district),
    description: name, folder: FOLDER, fileNamePrefix: name, region: region,
    crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});
}
expRaw(ndviG, 'raw_NDVI'); expRaw(lstG, 'raw_LST_degC'); expRaw(precG, 'raw_PREC_mm');
expRaw(elevG, 'raw_ELEV_m'); expRaw(slopeG, 'raw_SLOPE_deg');

// (Map preview removed: drawing the 10 m mask in the browser exceeds Earth Engine's interactive memory; exports are unaffected.)
Map.addLayer(district, {color: 'green'}, 'Kavre boundary');
