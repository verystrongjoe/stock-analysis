"""
This script should provide sytnax to connect flask-restful to a postgres db.
"""

import codecs
import io
import pdb
import os
import tempfile
import datetime      as dt
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import api.persist.pg as pg

db = pg.Postgre('postgres://tkrapi:tkrapi@127.0.0.1/tkrapi')

def getfeat(tkr):
  """This function should return a DataFrame full of features for a tkr."""
  sql_s  = "SELECT csv FROM features WHERE tkr = %s LIMIT 1"
  result = db.execute_select_sql(sql_s,[tkr])
  if not result.rowcount:
    return pd.DataFrame() # empty DF offers consistent behavior to caller.
  myrow  = [row for row in result][0]
  feat_df = pd.read_csv(io.StringIO(myrow.csv))
  return feat_df

def getfeatures():
  """This function should return a list of features."""
  sql_s  = "SELECT csv FROM features WHERE tkr = '^GSPC' LIMIT 1"
  result = db.execute_select_sql(sql_s)
  if not result.rowcount:
    return ['no features found'] # Probably, a problem.
  myrow     = [row for row in result][0]
  feat_df   = pd.read_csv(io.StringIO(myrow.csv))
  columns_l = feat_df.columns.tolist()
  # I should remove cdate, cp, pct_lead:
  return columns_l[3:]

def check_features(f_s):
  """This function should check validity of f_s user input."""
  valid_features_l = getfeatures()
  features_s       = f_s.replace("'","").replace('"','')
  features_st      = set(features_s.split(','))
  goodfeatures_st  = set(valid_features_l).intersection(features_st)
  goodfeatures_s   = ','.join(goodfeatures_st)
  return goodfeatures_s

def tkrinfo(tkr):
  """This function should return info about a tkr."""
  feat_df             = getfeat(tkr)
  if feat_df.empty:
    return {'tkr': ('No info for: '+tkr)}
  observation_count_i = int(feat_df.cdate.size)
  maxdate_row = feat_df.loc[feat_df.cdate == feat_df.cdate.max()]
  return {
    'tkr':                 tkr
    ,'observation_count':  observation_count_i
    ,'years_observations': np.round(observation_count_i/252.0,1)
    ,'mindate':            feat_df.cdate.min()
    ,'maxdate':            feat_df.cdate.max()
    ,'maxdate_price':      maxdate_row.cp.tolist()[0]
  }

def get_train_test(tkr,yrs,mnth,features):
  """Using tkr,yrs,mnth,features, this function should get train,test numpy arrays."""
  xtrain_a = np.array(())
  ytrain_a = np.array(())
  xtest_a  = np.array(())
  out_df   = pd.DataFrame()
  feat_df  = getfeat(tkr)

  if (feat_df.empty):
    # I should return empty objects:
    return xtrain_a, ytrain_a, xtest_a, out_df

  test_bool_sr = (feat_df.cdate.str[:7] == mnth)
  test_df      =  feat_df.loc[test_bool_sr] # should be about 21 rows

  if (test_df.empty):
    # I should return empty objects:
    return xtrain_a, ytrain_a, xtest_a, out_df

  # I should get the training data from feat_df:
  max_train_loc_i = -1 + test_df.index[0]
  min_train_loc_i = max_train_loc_i - yrs * 252

  if (min_train_loc_i < 10):
    # I should return empty objects:
    return xtrain_a, ytrain_a, xtest_a, out_df
  train_df = feat_df.loc[min_train_loc_i:max_train_loc_i]

  # I should train:
  features_l = features.split(',')
  xtrain_df  = train_df[features_l]
  xtrain_a   = np.array(xtrain_df)
  ytrain_a   = np.array(train_df)[:,2 ]
  xtest_df   = test_df[features_l]
  xtest_a    = np.array(xtest_df)
  out_df     = test_df.copy()[['cdate','cp','pct_lead']]
  return xtrain_a, ytrain_a, xtest_a, out_df

def getmonths4tkr(tkr,yrs):
  """Should return a List of mnth-strings suitable for learning from yrs years."""
  # I should get feat_df for tkr:
  feat_df = getfeat(tkr)
  if (feat_df.empty):
    # I should return empty List:
    return []
  # I should get a series of month-strings from feat_df.cdate
  mnth_sr = feat_df.cdate.str[:7] # Like: 2010-07
  mnth_a  = mnth_sr.unique() # Actually just unique values.
  mnth_l  = sorted(mnth_a.tolist())
  start_i     = 2+yrs*12 # I should start learning 2 months after yrs years.
  shortmnth_l = mnth_l[start_i:] # Should have enough history for learning.
  return shortmnth_l

def predictions2db(tkr,yrs,mnth,features,algo,predictions_df,kmodel,algo_params='None Needed'):
  """This function should copy predictions and reporting columns to db."""
  if kmodel: # If I am using keras.
    kmodel.save('/tmp/kmodel.h5')
    with open('/tmp/kmodel.h5','rb') as fh:
      kmodel_h5 = fh.read() # kmodel_h5 s.b. different than kmodel
  else: # I am not using keras.
    kmodel_h5   = None # db should convert this to NULL during INSERT.
  # I should convert DF to a string
  csv_s = predictions_df.to_csv(index=False,float_format='%.3f')
  # I should move CREATE TABLE to an initialization script.
  # Running this statement frequently is inefficient:
  sql_s = '''CREATE TABLE IF NOT EXISTS
    predictions(
    tkr          VARCHAR
    ,yrs         INTEGER
    ,mnth        VARCHAR
    ,features    VARCHAR
    ,algo        VARCHAR
    ,algo_params VARCHAR
    ,csv         TEXT
    ,kmodel_h5   BYTEA
  )'''
  db.execute_select_sql(sql_s) # should be ok for now.
  # Eventually I should replace DELETE/INSERT with UPSERT:
  sql_s = '''DELETE FROM predictions
    WHERE tkr         = %s
    AND   yrs         = %s
    AND   mnth        = %s
    AND   features    = %s
    AND   algo        = %s
    AND   algo_params = %s
    '''
  db.execute_select_sql(sql_s,[tkr,yrs,mnth,features,algo,algo_params])
  # I should match %s tokens with each column:
  sql_s = '''INSERT INTO predictions(
    tkr, yrs,mnth,features,algo,algo_params,csv  ,kmodel_h5)VALUES(
    %s , %s ,%s  ,%s      ,%s  ,%s         ,%s   ,%s)'''
  db.execute_select_sql(sql_s,[
    tkr, yrs,mnth,features,algo,algo_params,csv_s,kmodel_h5])
  return True

'bye'
