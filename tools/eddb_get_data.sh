#!/bin/bash
# Author: Javier Arellano-Verdejo (J@Vo)
# Email: <javier_arellano_verdejo@hotmail.com>
# Date: 2017/01/30
# Version: 0.1

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%% Database directory %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
DBDIR=db       # select name for data base files dir
DOWNLOAD=tmp   # select name for temporal download dir

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Database name %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
DBNAME=elite

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Download log %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
LOGFILE=$DBDIR/log/download.log # name of log file

# %%%%%%%%%%%%%%%%%%%%%%%%%%% Files to be download  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Contains all systems without faction information.
SYSTEMS=https://eddb.io/archive/v5/systems.csv

# Contains systems that changed or have been created within the past 7 days.
# Without faction information.
SYSTEMS_RECENTLY=https://eddb.io/archive/v5/systems_recently.csv

# Contains all populated systems, includes faction information.
SYSTEMS_POPULATED=https://eddb.io/archive/v5/systems_populated.jsonl

# Bodies
BODIES=https://eddb.io/archive/v5/bodies.jsonl

# Stations
STATIONS=https://eddb.io/archive/v5/stations.jsonl

# Minor Factions
MINOR_FACTIONS=https://eddb.io/archive/v5/factions.jsonl

# Prices
PRICES=https://eddb.io/archive/v5/listings.csv

# Commodity Reference
COMODITY=https://eddb.io/archive/v5/commodities.json

# Module Reference
MODULES=https://eddb.io/archive/v5/modules.json

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Support Functions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function download {
   echo -n "- Downloading $1 file ... "
   wget -q -P $DBDIR/$DOWNLOAD $2
   DATE=`date +%Y-%m-%d:%H:%M:%S`
   if [ $? -eq 0 ]; then
      echo "[OK]"
      mv ./$DBDIR/$DOWNLOAD/${2##*/} ./$DBDIR
      echo "$DATE OK $2 " >> $LOGFILE
   else
      echo "[ERROR]"
      echo "$DATE ERROR $2 " >> $LOGFILE
   fi
}

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Donwload Files %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Temporal directory to store files from server
rm -rf $DBDIR/$DOWNLOAD/*

# Initial Message
echo "EDDB - Elite: Dangerous Database Updating System V0.1"
echo "*** Downloading files from <eddb.io>"

# Download files
download "Systems" $SYSTEMS
download "recently changed systems" $SYSTEMS_RECENTLY
download "populated systems" $SYSTEMS_POPULATED
download "bodies" $BODIES
download "stations" $STATIONS
download "minor factions" $MINOR_FACTIONS
download "prices" $PRICES
download "commodity reference" $COMODITY
download "module reference" $MODULES

echo "*** Download complete"

# %%%%%%%%%%%%%%%%%%%%%%%%%%% Upload data to MongoDG %%%%%%%%%%%%%%%%%%%%%%%%%%%

echo "*** Updating 'elite' database"
# from 'jsonl' files
mongoimport --db $DBNAME --collection bodies --drop --file ./db/bodies.jsonl
mongoimport --db $DBNAME --collection factions --drop --file db/factions.jsonl
mongoimport --db $DBNAME --collection stations --drop --file ./db/db/stations.jsonl
mongoimport --db $DBNAME --collection systems_populated --drop --file db/systems_populated.jsonl
mongoimport --db $DBNAME --collection commodities --jsonArray --drop --file db/commodities.json
mongoimport --db $DBNAME --collection modules --jsonArray --drop --file db/modules.json

# from 'csv' files
mongoimport -d $DBNAME -c listings --type csv --drop --file db/listings.csv --headerline
mongoimport -d $DBNAME -c systems --type csv --drop --file db/systems.csv --headerline
mongoimport -d $DBNAME -c systems --type csv --mode upsert --file db/systems_recently.csv --headerline

echo "Done ;)"
