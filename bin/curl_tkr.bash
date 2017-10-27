#!/bin/bash

# curl_tkr.bash

# Demo:
# ./curl_tkr.bash IBM

# This script should call curl and help me study the response.

if [ "$#" -ne 1 ]
then
    echo You should supply a Ticker.
    echo Demo:
    echo $0 IBM
    exit 1
fi

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

TKR=$1
echo Busy with: $TKR
mkdir -p $TKRCSVD $TKRCSVH $TKRCSVS
CJAR=/tmp/curl_tkr.bash.cookiejar.txt

rm -f ${CJAR}

# Note the user-agent arg.
# I need to pass a string; variable with string fails.

/usr/bin/curl --verbose \
              --cookie-jar ${CJAR} \
              --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' \
              https://finance.yahoo.com/quote/${TKR} \
              > /tmp/tkr0.html \
              2> /tmp/s0.txt

sleep 2

/usr/bin/curl --verbose \
              --cookie     ${CJAR} \
              --cookie-jar ${CJAR} \
              --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' \
              https://finance.yahoo.com/quote/${TKR}/history?p=${TKR} \
              > /tmp/tkr1.html \
              2> /tmp/s1.txt

# In /tmp/tkr1.html I should see text like this near CrumbStore
# "CrumbStore":{"crumb":"z6M4ACgDGXK"}

# sed -n means ignore lines which do not match
# I should match text left of 'CrumbStore'
# I should match text right of '"}'
crum=`sed -n '/CrumbStore/s/^.*CrumbStore":{"crumb":"//p' /tmp/tkr1.html | sed -n '1s/"}.*//p'`
#sed -n '/CrumbStore/s/^.*CrumbStore":{"crumb":"//p' /tmp/tkr1.html|sed -n '1s/"}.*//p' > /tmp/c.txt

sleep 3

# https://query1.finance.yahoo.com/v7/finance/download/IBM?period1=-631123200&period2=1501743600&interval=1d&events=history&crumb=9cxzOy3G0UF

# I should get the current time as a unix time string:
nowutime=`date +%s`

# I should create some URLs which allow me to GET the CSV data:
QURL0="https://query1.finance.yahoo.com/v7/finance/download/${TKR}?"
QURLD="${QURL0}period1=-631123200&period2=${nowutime}&interval=1d&events=div&crumb=${crum}"
QURLH="${QURL0}period1=-631123200&period2=${nowutime}&interval=1d&events=history&crumb=${crum}"
QURLS="${QURL0}period1=-631123200&period2=${nowutime}&interval=1d&events=split&crumb=${crum}"

# I should get csv files now:

# Dividends:
/usr/bin/curl --verbose \
              --cookie     ${CJAR} \
              --cookie-jar ${CJAR} \
              --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' \
              $QURLD \
              > ${TKRCSVD}/${TKR}.csv \
              2> /tmp/s2.txt
sleep 1

# History:
/usr/bin/curl --verbose \
              --cookie     ${CJAR} \
              --cookie-jar ${CJAR} \
              --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' \
              $QURLH \
              > ${TKRCSVH}/${TKR}.csv \
              2> /tmp/s2.txt
sleep 1

# Splits:
/usr/bin/curl --verbose \
              --cookie     ${CJAR} \
              --cookie-jar ${CJAR} \
              --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' \
              $QURLS \
              > ${TKRCSVS}/${TKR}.csv \
              2> /tmp/s2.txt
# Files look okay?
ls -l ${TKRCSVD}/${TKR}.csv ${TKRCSVH}/${TKR}.csv ${TKRCSVS}/${TKR}.csv

# I should remove null-strings:
sed -i '/null/d' ${TKRCSVH}/${TKR}.csv

exit
