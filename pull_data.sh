if [ ! -f data/sidewalks_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/52n9-sdep/rows.csv?date=20240814&accessType=DOWNLOAD' -O data/sidewalks_nyc.csv; fi

# nyc 2020 ntas 
if [ ! -f data/ntas_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/9nt8-h7nd/rows.csv?accessType=DOWNLOAD' -O data/ntas_nyc.csv; fi

# nyc 2020 census blocks 
if [ ! -f data/nyc_cbs.zip ]; then wget 'https://s-media.nyc.gov/agencies/dcp/assets/files/zip/data-tools/bytes/nycb2020_24c.zip' -O data/nyc_cbs.zip; fi

# nyc Sidewalk cleanliness scorecard 
# https://data.cityofnewyork.us/City-Government/Scorecard-Ratings/rqhp-hivt/about_data

# ny satellite availability 
# https://broadbandmap.fcc.gov/data-download/nationwide-data?version=dec2023

# 5g map 
if [ ! -f data/5g_map.csv ]; then wget 'https://www.speedtest.net/s/ookla-5g-map/archive' -O data/5g_map.csv; fi

# 2023/12 nyc citibike data 
if [ ! -f data/citibike_202312_nyc.csv.zip ]; then wget 'https://s3.amazonaws.com/tripdata/JC-202312-citibike-tripdata.csv.zip' -O data/citibike_202312.csv.zip; fi

# nyc pedestrian curb ramp
if [ ! -f data/pedestrian_curb_ramp_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/ufzp-rrqu/rows.csv?accessType=DOWNLOAD' -O data/pedestrian_curb_ramp_nyc.csv; fi 

# surveillance cameras from surveilling surveillance paper 
if [ ! -f data/surveillance_cameras.zip ]; then wget 'https://storage.googleapis.com/scpl-surveillance/camera-data.zip' -O data/surveillance_cameras.zip; fi


# nyc raised crosswalk locations 
if [ ! -f data/raised_crosswalks_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uh2s-ftgh/rows.csv?accessType=DOWNLOAD' -O data/raised_crosswalks_nyc.csv; fi

# nyc VZW enhanced crossings locations 
if [ ! -f data/vzw_enhanced_crossings_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/k9a2-vdr8/rows.csv?accessType=DOWNLOAD' -O data/vzw_enhanced_crossings_nyc.csv; fi

# nyc zoning shapefile 
if [ ! -f data/zoning_nyc ]; then wget 'https://data.cityofnewyork.us/api/geospatial/kdig-pewd?method=export&format=Shapefile' -O data/zoning_nyc.zip; fi
# unzip, remove folder if already exists 
if [ -d data/zoning_nyc ]; then rm -r data/zoning_nyc; fi
unzip data/zoning_nyc.zip -d data/zoning_nyc
# remove .zip 
rm data/zoning_nyc.zip

# nyc 1 foot dem integer raster 
if [ ! -f data/1ft_dem_nyc ]; then wget 'https://sa-static-customer-assets-us-east-1-fedramp-prod.s3.amazonaws.com/data.cityofnewyork.us/NYC_DEM_1ft_Int.zip' -O data/1ft_dem_nyc.zip; fi
# unzip, remove folder if already exists
if [ -d data/1ft_dem_nyc ]; then rm -r data/1ft_dem_nyc; fi
unzip data/1ft_dem_nyc.zip -d data/1ft_dem_nyc
# remove .zip
rm data/1ft_dem_nyc.zip

# nyc pois 
if [ ! -f data/pois_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/t95h-5fsr/rows.csv?accessType=DOWNLOAD' -O data/pois_nyc.csv; fi

# will retain clutter from claustrophobic streets analysis 

# nyc bike lanes (weirdly unavailable for download right now)
# if [ ! -f data/bike_lanes.zip ]; then wget 'https://data.cityofnewyork.us/api/views/7vsa-caz7/rows.csv?accessType=DOWNLOAD' -O data/bike_lanes.zip; fi




# STREET CLUTTER 

# nyc in service alarm box locations 
# https://data.cityofnewyork.us/Public-Safety/In-Service-Alarm-Box-Locations/v57i-gtxb/about_data
# NOT DOWNLOADABLE THROUGH WGET 

# public recycling bins 
# https://data.cityofnewyork.us/Environment/Public-Recycling-Bins/sxx4-xhzg/about_data
# NOT DOWNLOADABLE THROUGH WGET

# dsny litter baskets 
if [ ! -f data/street_furniture/dsny_litter_baskets_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/8znf-7b2c/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/dsny_litter_baskets_nyc.csv; fi

# nyc fire hydrants 
if [ ! -f data/street_furniture/fire_hydrants_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/5bgh-vtsn/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/fire_hydrants_nyc.csv; fi

# nyc bus stop shelters 
if [ ! -f data/street_furniture/bus_stop_shelters_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/t4f2-8md7/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/bus_stop_shelters_nyc.csv; fi

# nyc linknyc kiosks 
# https://data.cityofnewyork.us/Social-Services/LinkNYC-Kiosk-Locations/s4kf-3yrf/about_data
# NOT DOWNLOADABLE THROUGH WGET

# nyc bicycle parking shelters 
if [ ! -f data/street_furniture/bicycle_parking_shelters_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/dimy-qyej/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/bicycle_parking_shelters_nyc.csv; fi

# nyc bicycle racks 
if [ ! -f data/street_furniture/bicycle_racks_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/geospatial/yh4a-g3fj?method=export&format=Original' -O data/street_furniture/bicycle_racks_nyc.csv; fi

# nyc citybench 
if [ ! -f data/street_furniture/citybench_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/kuxa-tauh/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/citybench_nyc.csv; fi

# nyc forestry tree points 
if [ ! -f data/street_furniture/forestry_tree_points_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/uvpi-gqnh/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/forestry_tree_points_nyc.csv; fi

# nyc newsstands 
if [ ! -f data/street_furniture/newsstands_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/w9zq-xm8b/rows.csv?accessType=DOWNLOAD' -O data/street_furniture/newsstands_nyc.csv; fi

# nyc parking meters 
if [ ! -f data/street_furniture/parking_meters_nyc.csv ]; then wget 'https://data.cityofnewyork.us/api/views/693u-uax6/rows.csv?date=20240816&accessType=DOWNLOAD' -O data/street_furniture/parking_meters_nyc.csv; fi

# nyc current street sign work orders 
# https://data.cityofnewyork.us/Transportation/Street-Sign-Work-Orders/qt6m-xctn/explore/query/SELECT%0A%20%20%60order_number%60%2C%0A%20%20%60record_type%60%2C%0A%20%20%60order_type%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60on_street%60%2C%0A%20%20%60on_street_suffix%60%2C%0A%20%20%60from_street%60%2C%0A%20%20%60from_street_suffix%60%2C%0A%20%20%60to_street%60%2C%0A%20%20%60to_street_suffix%60%2C%0A%20%20%60side_of_street%60%2C%0A%20%20%60order_completed_on_date%60%2C%0A%20%20%60sign_code%60%2C%0A%20%20%60sign_description%60%2C%0A%20%20%60sign_size%60%2C%0A%20%20%60sign_design_voided_on_date%60%2C%0A%20%20%60sign_location%60%2C%0A%20%20%60distance_from_intersection%60%2C%0A%20%20%60arrow_direction%60%2C%0A%20%20%60facing_direction%60%2C%0A%20%20%60sheeting_type%60%2C%0A%20%20%60support%60%2C%0A%20%20%60sign_notes%60%2C%0A%20%20%60sign_x_coord%60%2C%0A%20%20%60sign_y_coord%60%0AWHERE%20caseless_one_of%28%60record_type%60%2C%20%22Current%22%29/page/filter
# NOT DOWNLOADABLE THROUGH WGET


# nyc bollards 
# https://data.cityofnewyork.us/Transportation/Traffic-Bollards-Tracking-and-Installations/3f5t-9dqu/about_data
# NOT DOWNLOADABLE THROUGH WGET

