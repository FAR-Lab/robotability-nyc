if [ ! -f data/nyc_sidewalks.csv ]; then wget 'https://data.cityofnewyork.us/api/views/52n9-sdep/rows.csv?date=20240814&accessType=DOWNLOAD' -O data/nyc_sidewalks.csv; fi

# nyc Sidewalk cleanliness scorecard 
# https://data.cityofnewyork.us/City-Government/Scorecard-Ratings/rqhp-hivt/about_data

# ny satellite availability 
# https://broadbandmap.fcc.gov/data-download/nationwide-data?version=dec2023

# 5g map 
if [ ! -f data/5g_map.csv ]; then wget 'https://www.speedtest.net/s/ookla-5g-map/archive' -O data/5g_map.csv; fi

# 2023/12 nyc citibike data 
if [ ! -f data/citibike_202312.csv ]; then wget 'https://s3.amazonaws.com/tripdata/JC-202312-citibike-tripdata.csv.zip' -O data/citibike_202312.csv.zip; fi

# nyc pedestrian curb ramp
if [ ! -f data/nyc_pedestrian_curb_ramp.csv ]; then wget 'https://data.cityofnewyork.us/api/views/ufzp-rrqu/rows.csv?accessType=DOWNLOAD' -O data/nyc_pedestrian_curb_ramp.csv; fi 

# surveillance cameras from surveilling surveillance paper 
if [ ! -f data/surveillance_cameras.zip ]; then wget 'https://storage.googleapis.com/scpl-surveillance/camera-data.zip' -O data/surveillance_cameras.zip; fi

# nyc forestry tree points 
if [ ! -f data/nyc_forestry_tree_points.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uvpi-gqnh/rows.csv?accessType=DOWNLOAD' -O data/nyc_forestry_tree_points.csv; fi

# nyc raised crosswalk locations 
if [ ! -f data/nyc_raised_crosswalk.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uh2s-ftgh/rows.csv?accessType=DOWNLOAD' -O data/nyc_raised_crosswalk.csv; fi

# nyc VZW enhanced crossings locations 
if [ ! -f data/nyc_vzw_enhanced_crossings.csv ]; then wget 'https://data.cityofnewyork.us/api/views/k9a2-vdr8/rows.csv?accessType=DOWNLOAD' -O data/nyc_vzw_enhanced_crossings.csv; fi

# nyc zoning shapefile 
if [ ! -f data/nyc_zoning.zip ]; then wget 'https://data.cityofnewyork.us/api/geospatial/kdig-pewd?method=export&format=Shapefile' -O data/nyc_zoning.zip; fi

# nyc 1 foot dem integer raster 
if [ ! -f data/nyc_1ft_dem.zip ]; then wget 'https://sa-static-customer-assets-us-east-1-fedramp-prod.s3.amazonaws.com/data.cityofnewyork.us/NYC_DEM_1ft_Int.zip' -O data/nyc_1ft_dem.zip; fi

# nyc pois 
if [ ! -f data/nyc_pois.zip ]; then wget 'https://data.cityofnewyork.us/api/views/t95h-5fsr/rows.csv?accessType=DOWNLOAD' -O data/nyc_pois.zip; fi

# will retain clutter from claustrophobic streets analysis 

# nyc bike lanes (weirdly unavailable for download right now)
# if [ ! -f data/nyc_bike_lanes.zip ]; then wget 'https://data.cityofnewyork.us/api/views/7vsa-caz7/rows.csv?accessType=DOWNLOAD' -O data/nyc_bike_lanes.zip; fi