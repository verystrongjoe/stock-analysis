import glob
import os
import pandas as pd
import api.persist.pg as pg

def copy2db(tkrdir, target_db_url) :

    tkrhdir = tkrdir + '\\history'
    tkrddir = tkrdir + '\\div'
    tkrsdir = tkrdir + '\\split'

    # setup db connection
    db = pg.Postgre(target_db_url)

    # create table
    sql1 = "drop table if exists tkrprices"
    db.execute_select_sql(sql1)

    sql2 = "create table tkrprices(tkr varchar, csvd text, csvh text, csvs text)"
    db.execute_select_sql(sql2)

    # gathering csv to import into database
    for csvf_s in sorted(glob.glob(tkrhdir+'/*.csv')):

      sz_i = os.path.getsize(csvf_s)
      #print(csvf_s, sz_i)

      if (sz_i > 140):
        tkr0_s = csvf_s.split('\\')[-1].split('.')[0] # get ticker name

        try :
            csv_df = pd.read_csv(csvf_s)

        except :
            print(csvf_s + ' failed to read as a csv file')


        # I should convert to String and pick only two columns:
        csv0_s = csv_df.to_csv(index=False,header=False,columns=('Date','Close'),float_format='%.3f')
        csvh_s  = "'"+csv0_s+"'"
        tkr_s   = "'"+tkr0_s+"'"

        csvfd_s = tkrddir+'\\'+tkr0_s+'.csv'
        csvfs_s = tkrsdir+'\\'+tkr0_s+'.csv'

        try :
            csvd0_s = pd.read_csv(csvfd_s).sort_values('Date').to_csv(index=False,header=False)
        except:
            print(csvf_s + ' failed to read as a csv file')
        try:
            csvs0_s = pd.read_csv(csvfs_s).sort_values('Date').to_csv(index=False, header=False)
        except:
            print(csvfs_s + ' failed to read as a csv file')

        csvd_s  = "'"+csvd0_s+"'"
        csvs_s  = "'"+csvs0_s+"'"
        sql_s   = "insert into tkrprices(tkr,csvd,csvh,csvs)values("+tkr_s+","+csvd_s+","+csvh_s+","+csvs_s+")"
        db.execute_select_sql(sql_s)

        sql_check = "select tkr, csvh from tkrprices limit 1;"
        result = db.execute_select_sql(sql_check)

        'bye'