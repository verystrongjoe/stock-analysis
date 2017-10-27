-- after csv2db.py
select tkr, csvh from tkrprices limit 1;

select       tkr  from tkrprices;

select count(tkr) from tkrprices;

select csvh from tkrprices where tkr='SNAP'

select substring(csvh from 0 for 144) from tkrprices where tkr='SNAP'

select tkr, substring(csvh from 0 for 22) from tkrprices;

select tkr, csvs from tkrprices WHERE tkr = 'AAPL'

select tkr, csvd from tkrprices WHERE tkr = 'AAPL'


-- after genf.py
select       tkr  from features;
select count(tkr) from features;
select tkr,csv from features limit 1;

select tkr, length(csv) from features where tkr = '^GSPC';
select tkr, substring(csv for 256) from features where tkr = '^GSPC';

