#!/bin/bash

# retry_request_tkr.bash

# This script should loop through a folder full of CSV files and maybe feed some to request_tkr.bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

mkdir -p $TKRCSVD $TKRCSVH $TKRCSVS

date

# In bash how to loop through a folder of files?
for FN in ${TKRCSVH}/*.csv
do
    fsz_s=`ls -1s $FN | cut -c1-3`
    if [ "$fsz_s" = '4 /' ]
    then
	echo This file should be larger:
	ls -l $FN
	echo I should retry to request it:
	TKR=`basename $FN | sed 's/.csv//'`
	$PYTHON ${PYTHONPATH}/request_tkr.py $TKR
        # I should remove null-strings:
        sed -i '/null/d' ${TKRCSVH}/${TKR}.csv
    fi
done

date

exit
