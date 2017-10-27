#!/bin/bash

# retry_curl_tkrs.bash

# This script should loop through a folder full of CSV files and maybe feed some to curl_tkr.bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

# In bash how to loop through a folder of files?
for FN in ${TKRCSVH}/*.csv
do
    fsz_s=`ls -1s $FN | cut -c1-3`
    if [ "$fsz_s" = '4 /' ]
    then
	echo This file should be larger:
	ls -l $FN
	echo I should retry to curl it:
	TKR=`basename $FN | sed 's/.csv//'`
        ${SCRIPTPATH}/curl_tkr.bash $TKR
    fi
done
    
exit
