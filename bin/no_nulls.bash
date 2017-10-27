#!/bin/bash

# no_nulls.bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd ${SCRIPTPATH}/../
. env.bash

# I should remove null-strings from price-history csv-files:

cd $TKRCSVH
grep null *.csv

for FN in *.csv
do
  sed -i '/null/d' $FN
done

exit

