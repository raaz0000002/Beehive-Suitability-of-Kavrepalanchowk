// Precipitation for the apiary model: WorldClim V1 monthly precipitation normals 1960-1990
// (Hijmans et al. 2005, doi:10.1002/joc.1276), the same product and period as the air-temperature layer.
// Annual total = sum of the 12 monthly means (mm). Exported on the same 10 m grid as every other layer.
// Paste into code.earthengine.google.com, press Run, then in the Tasks tab click RUN on 'raw_PREC_WC_mm'.
// When the file appears in Google Drive (folder apiary_rasters), upload raw_PREC_WC_mm.tif to the project.
var BOUNDARY_ASSET = 'projects/extreme-clone-482209-b7/assets/kavre_boundary';
var CRS = 'EPSG:32645';
var GRID = [10, 0, 0, 0, -10, 0];
var DHULIKHEL = ee.Geometry.Point([85.5461, 27.6195]);

var district = ee.FeatureCollection(BOUNDARY_ASSET).filterBounds(DHULIKHEL).geometry();
print('District area km2 (should be about 1,394):', district.area(1).divide(1e6));
var region = district.transform(CRS, 1).bounds(1, CRS);

var wc = ee.ImageCollection('WORLDCLIM/V1/MONTHLY');
var prec = wc.select('prec').sum()                            // mm per year (no scale factor for prec)
  .setDefaultProjection(wc.first().projection())
  .resample('bilinear')
  .reproject({crs: CRS, crsTransform: GRID})
  .rename('prec');

prec.reduceRegion({reducer: ee.Reducer.minMax(), geometry: district, scale: 1000})
  .evaluate(function (r) { print('Annual precipitation range in Kavre (rough check, mm):', r); });

Export.image.toDrive({image: prec.toFloat().clip(district), description: 'raw_PREC_WC_mm',
  folder: 'apiary_rasters', fileNamePrefix: 'raw_PREC_WC_mm', region: region,
  crs: CRS, crsTransform: GRID, maxPixels: 1e10, fileFormat: 'GeoTIFF'});
Map.centerObject(district, 10);
Map.addLayer(district, {color: 'green'}, 'Kavre boundary');
