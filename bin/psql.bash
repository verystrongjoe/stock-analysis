#!/bin/bash

# psql.bash

PGPASSWORD=tkrapi psql -aP pager=no -U tkrapi -h 127.0.0.1 tkrapi $@

exit
