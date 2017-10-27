import io
import pdb
import os
import flask
import datetime      as dt
#import flask_restful as fr
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import keras
import api.pgdb as pgdb
import api.persist.pg as pg

# https://keras.io/models/model/#methods
batch_size_i = 256 # Doc: Number of samples per gradient update.
epochs_i     = 128 # Doc: Number of epochs to train the model.


# 케라스 사용함
def learn_predict_kerasnn(tkr       ='IBM'
                          , yrs      = 20  # years to train
                          , mnth     = '2016-11'  # Month to predict
                          , features = 'pct_lag1,slope4,moy'
                          , hl       = 2  # number of hidden layers
                          , neurons  = 4  # neurons in each hl
                          ):

  # 테스트데이터 카피본
  xtrain_a, ytrain_a, xtest_a, out_df = pgdb.get_train_test(tkr,yrs,mnth,features)

  if ((xtrain_a.size == 0) or (ytrain_a.size == 0) or (xtest_a.size == 0)):
    return out_df

  # 케라스 모델 정의
  kmodel     = keras.models.Sequential()

  # features들을 input layer에 정의
  features_l = features.split(',')
  features_i = len(features_l)
  kmodel.add(keras.layers.core.Dense(features_i, input_shape=(features_i,)))

  # 활성화 함수 정의
  kmodel.add(keras.layers.core.Activation('linear'))

  # Dropout 정의
  kmodel.add(keras.layers.core.Dropout(0.1)) 

  # 히든 레이어 정의
  for l_i in range(hl):
    kmodel.add(keras.layers.core.Dense(neurons))
    kmodel.add(keras.layers.core.Activation('linear'))
    kmodel.add(keras.layers.core.Dropout(0.1))

  # 아웃풋 레이어 정의
  kmodel.add(keras.layers.core.Dense(1)) 
  kmodel.add(keras.layers.core.Activation('linear'))
  kmodel.compile(loss='mean_squared_error', optimizer='adam')

  epochs_nn_i = 8 * epochs_i
  kmodel.fit(xtrain_a, ytrain_a, batch_size=batch_size_i, epochs=epochs_nn_i)

  # I should predict xtest_a then update out_df
  predictions_a           = np.round(kmodel.predict(xtest_a),3)

  out_df['prediction']    = [p_f[0] for p_f in predictions_a]
  out_df['effectiveness'] = np.sign(out_df.pct_lead*out_df.prediction)*np.abs(out_df.pct_lead)
  out_df['accuracy']      = (1+np.sign(out_df.effectiveness))/2
  algo                    = 'kerasnn'
  algo_params             = str([hl,neurons])

  # 데이터베이스 저장
  pgdb.predictions2db(tkr,yrs,mnth,features,algo,out_df,kmodel,algo_params)

  return out_df

def learn_predict_keraslinear(tkr='ABC',yrs=20,mnth='2016-11', features='pct_lag1,slope4,moy'):

  xtrain_a, ytrain_a, xtest_a, out_df = pgdb.get_train_test(tkr,yrs,mnth,features)

  if ((xtrain_a.size == 0) or (ytrain_a.size == 0) or (xtest_a.size == 0)):
    return out_df

  kmodel     = keras.models.Sequential()
  features_l = features.split(',')
  features_i = len(features_l)
  kmodel.add(keras.layers.core.Dense(features_i, input_shape=(features_i,)))
  kmodel.add(keras.layers.core.Activation('linear'))

  # I should have 1 linear-output:
  kmodel.add(keras.layers.core.Dense(1)) 
  kmodel.add(keras.layers.core.Activation('linear'))
  kmodel.compile(loss='mean_squared_error', optimizer='adam')
  kmodel.fit(xtrain_a,ytrain_a, batch_size=batch_size_i, epochs=epochs_i)

  # I should predict xtest_a then update out_df
  predictions_a           = np.round(kmodel.predict(xtest_a),3)

  # Done with Keras, I should pass along the predictions.
  predictions_l           = [p_f[0] for p_f in predictions_a] # I want a list
  out_df['prediction']    = predictions_l
  out_df['effectiveness'] = np.sign(out_df.pct_lead*out_df.prediction)*np.abs(out_df.pct_lead)
  out_df['accuracy']      = (1+np.sign(out_df.effectiveness))/2
  algo                    = 'keraslinear'

  # I should save my work to the db:
  pgdb.predictions2db(tkr,yrs,mnth,features,algo,out_df,kmodel)
  # I should return a DataFrame useful for reporting on the predictions.
  return out_df

def load_predict_keraslinear(tkr='FB',yrs=3,mnth='2017-08', features='pct_lag1,slope4,moy'):

  """This function should demo how to predict from a model in the db."""
  learn_predict_keraslinear(tkr,yrs,mnth,features) # Store a model in th db.

  db = pg.Postgre('postgres://tkrapi:tkrapi@127.0.0.1/tkrapi')

  sql_s = '''SELECT tkr,yrs,mnth,features,algo,algo_params, kmodel_h5
    FROM predictions
    WHERE tkr      = %s 
    AND   yrs      = %s
    AND   mnth     = %s
    AND   features = %s
    LIMIT 1'''

  result = db.execute_select_sql(sql_s,[tkr,yrs,mnth,features])

  if not result.rowcount:
    return ['no result'] # Probably, a problem.

  myrow     = [row for row in result][0]
  kmodel_h5 = (bytes(myrow.kmodel_h5))

  with open('/tmp/kmodel2.h5','wb') as fh:
    fh.write(kmodel_h5)
  kmodel = keras.models.load_model('/tmp/kmodel2.h5')
  
  xtrain_a, ytrain_a, xtest_a, out_df = pgdb.get_train_test(tkr,yrs,mnth,features)
  if ((xtrain_a.size == 0) or (ytrain_a.size == 0) or (xtest_a.size == 0)):
    return out_df # probably empty too.
  # Start using Keras here.
  # I should predict xtest_a then update out_df
  predictions_a           = np.round(kmodel.predict(xtest_a),3)
  # Done with Keras, I should pass along the predictions.
  predictions_l           = [p_f[0] for p_f in predictions_a] # I want a list
  out_df['prediction']    = predictions_l
  out_df['effectiveness'] = np.sign(out_df.pct_lead*out_df.prediction)*np.abs(out_df.pct_lead)
  out_df['accuracy']      = (1+np.sign(out_df.effectiveness))/2
  algo                    = 'keraslinear'
  
  return out_df

def learn_predict_keraslinear_yr(tkr='ABC',yrs=20,yr=2016, features='pct_lag1,slope4,moy'):
  """This function should use keras to learn and predict for a year."""
  empty_df = pd.DataFrame()
  yr_l     = [empty_df, empty_df] # Ready for pd.concat()
  # I should rely on monthy predictions:
  for mnth_i in range(1,13):
    mnth_s = str(mnth_i).zfill(2)
    mnth   = str(yr)+'-'+mnth_s
    m_df   = learn_predict_keraslinear(tkr,yrs,mnth, features)
    yr_l.append(m_df)
  # I should gather the monthy predictions:
  yr_df = pd.concat(yr_l, ignore_index=True)
  return yr_df

def learn_predict_keraslinear_tkr(tkr='ABC',yrs=20, features='pct_lag1,slope4,moy'):
  """This function should use keras to learn and predict for a tkr."""
  # From db, I should get a list of all months for tkr:
  mnth_l = pgdb.getmonths4tkr(tkr,yrs)
  # I should rely on monthy predictions:
  empty_df = pd.DataFrame()
  tkr_l    = [empty_df, empty_df] # Ready for pd.concat()
  for mnth_s in mnth_l:
    m_df = learn_predict_keraslinear(tkr,yrs,mnth_s, features)
    tkr_l.append(m_df)
  # I should gather the monthy predictions:
  tkr_df = pd.concat(tkr_l, ignore_index=True)
  return tkr_df

def learn_predict_kerasnn_yr(tkr    = 'FB'
                          ,yrs      = 3    # Years to train
                          ,yr       = 2017 # Predict this year
                          ,features = 'pct_lag1,slope4,moy'
                          ,hl       = 2 # number of hidden layers
                          ,neurons  = 4 # neurons in each hl
                          ):
  """This function should use keras to learn and predict for a year."""
  empty_df = pd.DataFrame()
  yr_l     = [empty_df, empty_df] # Ready for pd.concat()
  # I should rely on monthy predictions:
  for mnth_i in range(1,13):
    mnth_s = str(mnth_i).zfill(2)
    mnth   = str(yr)+'-'+mnth_s
    m_df   = learn_predict_kerasnn(tkr, yrs, mnth, features, hl, neurons)
    yr_l.append(m_df)
  # I should gather the monthy predictions:
  yr_df = pd.concat(yr_l, ignore_index=True)
  return yr_df

def learn_predict_kerasnn_tkr(tkr   = 'FB' # Predict all years for this tkr.
                          ,yrs      = 3    # years to train
                          ,features = 'pct_lag1,slope4,moy'
                          ,hl       = 2 # number of hidden layers
                          ,neurons  = 4 # neurons in each hl
                          ):
  """This function should use keras to learn and predict for a tkr."""
  # From db, I should get a list of all months, and thus all years, for tkr:
  mnth_l = pgdb.getmonths4tkr(tkr,yrs)
  # I should rely on monthy predictions:
  empty_df = pd.DataFrame()
  tkr_l    = [empty_df, empty_df] # Ready for pd.concat()
  for mnth_s in mnth_l:
    m_df = learn_predict_kerasnn(tkr, yrs, mnth_s, features)
    tkr_l.append(m_df)
  # I should gather the monthy predictions:
  tkr_df = pd.concat(tkr_l, ignore_index=True)
  return tkr_df

'bye'