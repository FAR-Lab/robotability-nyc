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
if [ ! -f data/surveillance_cameras.csv ]; then wget 'https://storage.googleapis.com/scpl-surveillance/camera-data.zip' -O data/surveillance_cameras.zip; fi

# nyc forestry tree points 
if [ ! -f data/nyc_forestry_tree_points.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uvpi-gqnh/rows.csv?accessType=DOWNLOAD' -O data/nyc_forestry_tree_points.csv; fi

# nyc raised crosswalk locations 
if [ ! -f data/nyc_raised_crosswalk.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uh2s-ftgh/rows.csv?accessType=DOWNLOAD' -O data/nyc_raised_crosswalk.csv; fi

# nyc VZW enhanced crossings locations 
if [ ! -f data/nyc_vzw_enhanced_crossings.csv ]; then wget 'https://data.cityofnewyork.us/api/views/k9a2-vdr8/rows.csv?accessType=DOWNLOAD' -O data/nyc_vzw_enhanced_crossings.csv; fi