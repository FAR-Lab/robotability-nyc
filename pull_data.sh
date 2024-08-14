if [ ! -f data/nyc_sidewalks.csv ]; then wget 'https://data.cityofnewyork.us/api/views/52n9-sdep/rows.csv?date=20240814&accessType=DOWNLOAD' -O data/nyc_sidewalks.csv; fi
