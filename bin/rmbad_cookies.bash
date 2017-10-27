#!/bin/bash

# rmbad_cookies.bash

# This script should rm csv files connected to Invalid cookies.

cd ~/tkrcsv/

grep cookie */*csv|awk -F / '{print $2}'|awk -F . '{print $1}'|sort -u|while read TKR
do
    #echo $TKR
    echo rm -f ~/tkrcsv/*/${TKR}.csv
    rm      -f ~/tkrcsv/*/${TKR}.csv
done


exit

