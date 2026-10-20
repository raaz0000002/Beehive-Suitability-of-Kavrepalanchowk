// ============================================================================
// WATER layer from MERIT Hydro streams (replaces the OpenStreetMap river layer).
// Paste into code.earthengine.google.com, press Run, then in the Tasks tab click RUN on
// both exports (WATER and raw_WATER_dist_m). Same grid, region and boundary as before,
// so the new WATER.tif drops straight into your rasters folder.
// Streams = MERIT Hydro cells with upstream drainage area >= STREAM_KM2 (Yamazaki et al. 2019).
// ============================================================================

// ---------------- 1. Settings ----------------
var BOUNDARY_ASSET = 'projects/YOUR-EE-PROJECT/assets/kavre_boundary';
var FOLDER = 'apiary_rasters';
var STREAM_KM2 = 1;      // stream threshold, km2 of upstream area (main run)

var CRS = 'EPSG:32645';
var GRID = [10, 0, 0, 0, -10, 0];

// ---------------- 2. District boundary (same rule as the main script) ----------------
var DHULIKHEL = ee.Geometry.Point([85.5461, 27.6195]);
var districtFC = ee.FeatureCollection(BOUNDARY_ASSET).filterBounds(DHULIKHEL);
var nB = districtFC.size().getInfo();
if (nB !== 1) { throw new Error('The boundary asset has ' + nB + ' polygons at Dhulikhel (expected 1).'); }
var district = districtFC.geometry();
print('District area km2 (should be about 1,394):', district.area(1).divide(1e6));
var region = district.transform(CRS, 1).bounds(1, CRS);
Map.centerObject(district, 10);

function onGrid(img) { return img.reproject({crs: CRS, crsTransform: GRID}); }

// ---------------- 3. Streams from MERIT Hydro ----------------
var merit = ee.Image('MERIT/Hydro/v1_0_1');
var upa = merit.select('upa');                       // upstream drainage area, km2
function streams(t) { return upa.gte(t).selfMask().clip(district.buffer(2000)); }

// ---------------- 4. Distance (m) and 1-9 score, 100 m bands as before ----------------
function distM(t) {
  return onGrid(streams(t)).unmask(0)
    .fastDistanceTransform(128, 'pixels', 'squared_euclidean').sqrt().multiply(10)
    .unmask(1e6)                                     // beyond 1.28 km scores 1 anyway
    .reproject({crs: CRS, crsTransform: GRID});      // keep the distance in 10 m cells at any zoom or scale
}
var dist = distM(STREAM_KM2);
var WATER = ee.Image(9).subtract(dist.divide(100).floor()).max(1);

// ---------------- 5. Check: share of the district 800 m or more from a stream ----------------
// (OSM gave 37.9%. Sampled every 100 m in the background so the page stays responsive.)
[0.5, 1, 2, 5].forEach(function (t) {
  distM(t).gte(800).reduceRegion({reducer: ee.Reducer.mean(), geometry: district, scale: 100,
    crs: CRS, maxPixels: 1e10, tileScale: 4})
    .evaluate(function (r, err) {
      if (err) { print('Check for ' + t + ' km2 could not finish (exports unaffected): ' + err); return; }
      var v = r[Object.keys(r)[0]];
      print('Threshold ' + t + ' km2: ' + (100 * v).toFixed(1) + '% of district is 800 m or more from a stream');
    });
});

// ---------------- 6. Export ----------------
Export.image.toDrive({image: WATER.unmask(0).toByte().clip(district),
  description: 'WATER', folder: FOLDER, fileNamePrefix: 'WATER', region: region,
  crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});
Export.image.toDrive({image: dist.min(5000).toFloat().clip(district),
  description: 'raw_WATER_dist_m', folder: FOLDER, fileNamePrefix: 'raw_WATER_dist_m', region: region,
  crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});

// Preview at MERIT's own resolution only (light enough for the browser)
Map.addLayer(streams(STREAM_KM2), {palette: ['0000ff']}, 'MERIT streams (' + STREAM_KM2 + ' km2)');
Map.addLayer(district, {color: 'green'}, 'Kavre boundary', true, 0.3);
