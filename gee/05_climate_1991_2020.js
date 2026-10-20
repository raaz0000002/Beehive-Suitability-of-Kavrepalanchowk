// Climate layers for the apiary model, 1991-2020 (replaces the 1960-1990 WorldClim normals).
//
// Main layers (1991-2020, ~1 km): change-factor ("delta") downscaling.
//   WorldClim V1 30-arc-second normals (Hijmans et al. 2005) give the terrain-resolved spatial pattern;
//   TerraClimate (Abatzoglou et al. 2018, CC0) gives the month-by-month change from 1961-1990 to 1991-2020:
//     temperature  T(1991-2020) = WorldClim T + [TerraClimate T(1991-2020) - TerraClimate T(1961-1990)]
//     precipitation P(1991-2020) = WorldClim P x [TerraClimate P(1991-2020) / TerraClimate P(1961-1990)]
//   Temperature = mean of the six honey-flow months (Mar-May, Sep-Nov; Neupane et al. 2024).
//   Precipitation = annual total (sum of 12 months).
// Sensitivity layers: TerraClimate 1991-2020 at its native ~4 km grid, and the original WorldClim 1960-1990.
//
// HOW TO RUN
//   1. Paste into code.earthengine.google.com and press Run. Check the numbers printed in the Console.
//   2. In the Tasks tab click RUN on the three exports (each is small, under 1 MB).
//   3. Download the three .tif files from Google Drive (folder apiary_rasters) and attach them in the chat.
//   Files are exported on the native climate grids; Python resamples them to the 10 m analysis grid
//   (bilinear) and scores them (scripts/02_prep_layers.py climate ...).

var BOUNDARY_ASSET = 'projects/extreme-clone-482209-b7/assets/kavre_boundary';
var DHULIKHEL = ee.Geometry.Point([85.5461, 27.6195]);
var FLOW = [3, 4, 5, 9, 10, 11];
var MONTHS = ee.List.sequence(1, 12);

var district = ee.FeatureCollection(BOUNDARY_ASSET).filterBounds(DHULIKHEL).geometry();
print('District area km2 (should be about 1,394):', district.area(1).divide(1e6));
var region = district.bounds(1).buffer(10000).bounds(1);   // 10 km margin so bilinear resampling has neighbours at the edge

// ---------- WorldClim V1 (1960-1990), 30 arc-seconds
var wc = ee.ImageCollection('WORLDCLIM/V1/MONTHLY');
var wcInfo = wc.first().projection().getInfo();   // {crs, transform} of the native WorldClim grid
function wcT(m) { return wc.filter(ee.Filter.eq('month', m)).first().select('tavg').multiply(0.1); }   // degC
function wcP(m) { return wc.filter(ee.Filter.eq('month', m)).first().select('prec'); }                 // mm

// ---------- TerraClimate monthly (1958-2024), 1/24 degree
var tc = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE');
var tcProj = tc.first().projection();
var tcInfo = tcProj.getInfo();
function tcSub(m, y0, y1) {
  return tc.filter(ee.Filter.calendarRange(y0, y1, 'year')).filter(ee.Filter.calendarRange(m, m, 'month'));
}
function tcT(m, y0, y1) {   // mean of (tmax + tmin) / 2, scale 0.1 -> degC
  var c = tcSub(m, y0, y1);
  return c.select('tmmx').mean().add(c.select('tmmn').mean()).multiply(0.05).setDefaultProjection(tcProj);
}
function tcP(m, y0, y1) { return tcSub(m, y0, y1).select('pr').mean().setDefaultProjection(tcProj); }   // mm/month
print('TerraClimate years 1961-1990 per month (expect 30):', tcSub(1, 1961, 1990).size());
print('TerraClimate years 1991-2020 per month (expect 30):', tcSub(1, 1991, 2020).size());

// ---------- change factors at ~4 km, resampled bilinearly onto the WorldClim grid
function dT(m) {   // additive change, computed on the TerraClimate grid, then interpolated bilinearly
  return tcT(m, 1991, 2020).subtract(tcT(m, 1961, 1990)).setDefaultProjection(tcProj).resample('bilinear');
}
function rP(m) {   // multiplicative change (denominator floored at 1 mm), same treatment
  return tcP(m, 1991, 2020).divide(tcP(m, 1961, 1990).max(1)).setDefaultProjection(tcProj).resample('bilinear');
}

var airtNew = ee.ImageCollection(FLOW.map(function (m) { return wcT(m).add(dT(m)); })).mean();
var precNew = ee.ImageCollection(MONTHS.map(function (m) { return wcP(m).multiply(rP(m)); })).sum();
var airtWC  = ee.ImageCollection(FLOW.map(function (m) { return wcT(m); })).mean();
var precWC  = ee.ImageCollection(MONTHS.map(function (m) { return wcP(m); })).sum();
var airtTC  = ee.ImageCollection(FLOW.map(function (m) { return tcT(m, 1991, 2020); })).mean();
var precTC  = ee.ImageCollection(MONTHS.map(function (m) { return tcP(m, 1991, 2020); })).sum();

var main1991 = airtNew.rename('airt_flow_degC').addBands(precNew.rename('prec_annual_mm')).toFloat();
var wc1960   = airtWC.rename('airt_flow_degC').addBands(precWC.rename('prec_annual_mm')).toFloat();
var tc1991   = airtTC.rename('airt_flow_degC').addBands(precTC.rename('prec_annual_mm')).toFloat();

// ---------- quick checks over the district (printed in the Console)
function stats(img, label, scale) {
  img.reduceRegion({reducer: ee.Reducer.minMax().combine(ee.Reducer.mean(), '', true),
                    geometry: district, scale: scale, maxPixels: 1e9})
     .evaluate(function (r) { print(label, r); });
}
stats(main1991, 'MAIN 1991-2020 (WorldClim pattern + TerraClimate change), ~1 km:', 1000);
stats(wc1960,   'WorldClim 1960-1990 (previous main layers), ~1 km:', 1000);
stats(tc1991,   'TerraClimate 1991-2020 native, ~4 km:', 4638.3);

// ---------- exports (native grids, EPSG:4326)
Export.image.toDrive({image: main1991, description: 'clim_1991_2020_main_wcgrid', folder: 'apiary_rasters',
  fileNamePrefix: 'clim_1991_2020_main_wcgrid', region: region, crs: wcInfo.crs, crsTransform: wcInfo.transform,
  maxPixels: 1e9, fileFormat: 'GeoTIFF'});
Export.image.toDrive({image: wc1960, description: 'clim_1960_1990_worldclim_wcgrid', folder: 'apiary_rasters',
  fileNamePrefix: 'clim_1960_1990_worldclim_wcgrid', region: region, crs: wcInfo.crs, crsTransform: wcInfo.transform,
  maxPixels: 1e9, fileFormat: 'GeoTIFF'});
Export.image.toDrive({image: tc1991, description: 'clim_1991_2020_terraclimate_native', folder: 'apiary_rasters',
  fileNamePrefix: 'clim_1991_2020_terraclimate_native', region: region, crs: tcInfo.crs, crsTransform: tcInfo.transform,
  maxPixels: 1e9, fileFormat: 'GeoTIFF'});

Map.centerObject(district, 10);
Map.addLayer(main1991.select('airt_flow_degC').clip(district), {min: 10, max: 26, palette: ['2c7bb6', 'ffffbf', 'd7191c']}, 'Air temp 1991-2020');
Map.addLayer(main1991.select('prec_annual_mm').clip(district), {min: 900, max: 2500, palette: ['f7fbff', '08306b']}, 'Precip 1991-2020', false);
Map.addLayer(ee.Image().paint(district, 0, 2), {palette: '000000'}, 'Kavre boundary');
