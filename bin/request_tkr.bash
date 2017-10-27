#!/bin/bash

# request_tkr.bash

# This script should call request_tkr.py
# which should help me collect prices into CSV files
# Demo:
# bin/request_tkr.bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

mkdir -p $TKRCSVD $TKRCSVH $TKRCSVS

date
cat ${PARPATH}/tkrlist.txt|while read TKR
do
    echo busy with                       $TKR
    $PYTHON ${PYTHONPATH}/request_tkr.py $TKR
    # I should remove null-strings:
    sed -i '/null/d' ${TKRCSVH}/${TKR}.csv
done
date

#debug
exit
#debug

${SCRIPTPATH}/retry_request_tkr.bash
${SCRIPTPATH}/retry_request_tkr.bash
${SCRIPTPATH}/retry_request_tkr.bash
${SCRIPTPATH}/retry_request_tkr.bash

exit
