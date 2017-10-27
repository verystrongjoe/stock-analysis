#!/bin/bash

# curl_tkrs.bash

# This script should loop through a text file full of tkrs and feed each to curl_tkr.bash

# cat ${PARPATH}/tkrlist.txt | while read TKR

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

cat ${PARPATH}/tkrlist.txt | while read TKR
do
    ${SCRIPTPATH}/curl_tkr.bash $TKR
done

# Some of the tkrs might need more effort

${SCRIPTPATH}/retry_curl_tkrs.bash
${SCRIPTPATH}/retry_curl_tkrs.bash
${SCRIPTPATH}/retry_curl_tkrs.bash
${SCRIPTPATH}/retry_curl_tkrs.bash

exit

./curl_tkr.bash AAPL
./curl_tkr.bash IBM
./curl_tkr.bash ^GSPC
./curl_tkr.bash ^RUT

exit
