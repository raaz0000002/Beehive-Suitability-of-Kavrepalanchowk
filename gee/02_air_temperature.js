// Air temperature for the apiary model: WorldClim V1 mean monthly temperature (Hijmans et al. 2005,
// doi:10.1002/joc.1276), averaged over the honey-flow months (Mar-May, Sep-Nov; Neupane et al. 2024).
// Exported in degrees C on the same 10 m grid as the other layers. Scoring to 1-9 is done afterwards.
var BOUNDARY_ASSET = 'projects/YOUR-EE-PROJECT/assets/kavre_boundary';
var CRS = 'EPSG:32645';
var GRID = [10, 0, 0, 0, -10, 0];
var DHULIKHEL = ee.Geometry.Point([85.5461, 27.6195]);

var district = ee.FeatureCollection(BOUNDARY_ASSET).filterBounds(DHULIKHEL).geometry();
print('District area km2 (should be about 1,394):', district.area(1).divide(1e6));
var region = district.transform(CRS, 1).bounds(1, CRS);

var wc = ee.ImageCollection('WORLDCLIM/V1/MONTHLY');
var airt = wc.filter(ee.Filter.inList('month', [3, 4, 5, 9, 10, 11]))
  .select('tavg').mean().multiply(0.1)                       // scale factor 0.1 -> degrees C
  .setDefaultProjection(wc.first().projection())
  .resample('bilinear')
  .reproject({crs: CRS, crsTransform: GRID})
  .rename('airt');

airt.reduceRegion({reducer: ee.Reducer.minMax(), geometry: district, scale: 1000})
  .evaluate(function (r) { print('Air temperature range in Kavre (rough check, degC):', r); });

Export.image.toDrive({image: airt.toFloat().clip(district), description: 'raw_AIRT_degC',
  folder: 'apiary_rasters', fileNamePrefix: 'raw_AIRT_degC', region: region,
  crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});
Map.centerObject(district, 10);
Map.addLayer(district, {color: 'green'}, 'Kavre boundary');
