"""
unsplit_prices.py

Note that this script is an artifact which I no longer use.
Before 2017-05, Yahoo served accurate historical closing prices.
That data had discontinuities at split dates.
After 2017-05, Yahoo serves adjusted prices so that the discontinuities are removed.
This script will become useful if I encounter unadjusted historical closing prices again.


This script should create a column named uscp which I see as unsplit_prices.

Given a splitdate, this script should find all prices at and after the splitdate.
Then uscp should be made from (cp * split_ratio).

Demo:
. env.bash
$PYTHON py/unsplit_prices.py
"""

import io
import os
import pdb
import pandas     as pd
import sqlalchemy as sql
from   fractions import Fraction

# I should connect to the db.
db_s = os.environ['PGURL']
conn = sql.create_engine(db_s).connect()

sql_s = "drop table if exists unsplit_prices"
conn.execute(sql_s)
sql_s = "create table unsplit_prices(tkr varchar, csvd text, csvh text, csvs text)"
conn.execute(sql_s)

# The data I need should be in a table named tkrprices
# which should have been created by py/pg.py
# which should have been called by bin/req2db.bash

# I should loop through the table full of tkrs, prices, splitdates:
sql_s   = "select tkr, csvd, csvh, csvs from tkrprices order by tkr" # where tkr like 'AA%'"
sql_sql = sql.text(sql_s)
result  = conn.execute(sql_sql)
if not result.rowcount:
  sys.exit(1)

for rowtkr in result:
  print(rowtkr.tkr)
  cp_df = pd.read_csv(io.StringIO(rowtkr.csvh),names=('cdate','cp'))
  sd_df = pd.read_csv(io.StringIO(rowtkr.csvs),names=('sdate','ratio'))
  # I should initialize unsplit prices to current prices:
  cp_df['uscp'] = cp_df.cp
  # For each tkr, the split dates should drive a loop:
  for rowsd in sd_df.itertuples():
    # I should create a Series full of Booleans:
    dt_gte_sd_sr = (cp_df.cdate >= rowsd.sdate)
    # Above series tells me dates after splitdate.
    # Prices at and after splitdate should be multiplied by splitratio.
    cp_df.loc[dt_gte_sd_sr,'uscp'] = float(Fraction(rowsd.ratio)) * cp_df[dt_gte_sd_sr].uscp
  print(sd_df)
  print(cp_df.tail(1))
  # I should insert uscp into db (along with other values from tkrprices):
  csvh_s = cp_df.to_csv(index=False,header=False,float_format='%.3f')
  csvh_s = "'"+csvh_s+"'"
  tkr_s  = "'"+rowtkr.tkr+"'"
  csvd_s = "'"+rowtkr.csvd+"'"
  csvs_s = "'"+rowtkr.csvs+"'"
  sql_s  = "insert into unsplit_prices(tkr,csvd,csvh,csvs)values("+tkr_s+","+csvd_s+","+csvh_s+","+csvs_s+")"
  conn.execute(sql_s)
'bye'
