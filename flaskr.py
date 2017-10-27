"""
localhost:5000/demo11.json
localhost:5000/static/hello.json
localhost:5000/demos

localhost:5000/features
localhost:5000/algo_demos
localhost:5000/tkrs
localhost:5000/tkrlist
localhost:5000/istkr/IBM
localhost:5000/tkrinfo/IBM
localhost:5000/years
localhost:5000/tkrprices/SNAP

localhost:5000/sklinear/ABC/20/2016-12/'pct_lag1,slope3,dow,moy'
localhost:5000/sklinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'
localhost:5000/sklinear_tkr/IBM/20/'pct_lag1,slope3,dow,moy'

localhost:5000/keraslinear/ABC/20/2016-12/'pct_lag2,slope5,dow,moy'
localhost:5000/keraslinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'
localhost:5000/keraslinear_tkr/IBM/20/'pct_lag1,slope3,dow,moy'

localhost:5000/keras_nn/IBM/25/2014-11?features='pct_lag1,slope4,moy'&hl=2&neurons=4
localhost:5000/keras_nn_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'
"""

import io
import pdb
import os
import datetime      as dt
import flask         as fl
import flask_restful as fr
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import sklearn.linear_model as skl
# modules in the py folder:
import api.pgdb as pgdb
import api.sktkr as sktkr
import api.kerastkr as kerastkr

# I should connect to the DB
db_s = 'postgres://tkrapi:tkrapi@127.0.0.1/tkrapi'
conn = sql.create_engine(db_s).connect()

homeDir = os.environ['HOME']
input = homeDir+'\\data\\input\\'

# I should ready flask_restful:
application = fl.Flask(__name__)
api         = fr.Api(application)

# I should fill lists which users want frequently:
with open(input+'years.txt') as fh:
  years_l = fh.read().split()
  
with open(input+'tkrlist.txt') as fh:
  tkrlist_l = fh.read().split()
  
class Demo11(fr.Resource):
  """
  This class should be a simple syntax demo.
  """
  def get(self):
    my_k_s = 'hello'
    my_v_s = 'world'
    return {my_k_s: my_v_s}
api.add_resource(Demo11, '/demo11.json')

class AlgoDemos(fr.Resource):
  """
  This class should return a list of Algo Demos.
  """
  def get(self):
    algo_demos_l = [
      "/sklinear/IBM/20/2017-08/'pct_lag1,slope3,dow,moy'"
      ,"/sklinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'"
      ,"/sklinear_tkr/IBM/20/'pct_lag1,slope3,dow,moy'"
      ,"/keraslinear/FB/3/2017-08/'pct_lag2,slope5,moy'"
      ,"/keraslinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'"
      ,"/keraslinear_tkr/IBM/20/'pct_lag1,slope3,dow,moy'"
      ,"/keras_nn/FB/3/2017-07?features='pct_lag1,slope4,moy'&hl=2&neurons=4"
      ,"/keras_nn_yr/FB/3/2017?features='pct_lag1,slope4,moy'&hl=2&neurons=4"
      ,"/keras_nn_tkr/FB/3?features='pct_lag1,slope4,moy'&hl=2&neurons=4"
    ]
    return {
      'algo_demos': algo_demos_l
      ,'features':  pgdb.getfeatures()
    }
api.add_resource(AlgoDemos, '/algo_demos')

class Demos(fr.Resource):
  """
  This class should return a list of Demos.
  """
  def get(self):
    demos_l = [
      "/demos"
      ,"/algo_demos"
      ,"/features"
      ,"/tkrs"
      ,"/tkrlist"
      ,"/years"
      ,"/tkrinfo/IBM"
      ,"/tkrprices/SNAP"
      ,"/istkr/YHOO"
      ,"/demo11.json"
      ,"/static/hello.json"
      ,AlgoDemos().get()
    ]
    return {'demos': demos_l}
api.add_resource(Demos, '/demos')

class Features(fr.Resource):
  """
  This class should return a list of available ML features.
  """
  def get(self):
    return {'features': pgdb.getfeatures()}
api.add_resource(Features, '/features')

class Tkrinfo(fr.Resource):
  """
  This class should return info about a tkr.
  """
  def get(self, tkr):
    tkrinfo   = None
    torf      = tkr in tkrlist_l
    if torf:
      tkrinfo = pgdb.tkrinfo(tkr)
    return {'istkr': torf,'tkrinfo': tkrinfo}
api.add_resource(Tkrinfo, '/tkrinfo/<tkr>')

class Tkrlist(fr.Resource):
  """
  This class should list all the tkrs in tkrlist.txt
  """
  def get(self):
    return {'tkrlist': tkrlist_l}
api.add_resource(Tkrlist, '/tkrlist')

class Tkrs(fr.Resource):
  """
  This class should list all the tkrs in tkrlist.txt
  """
  def get(self):
    return {'tkrs': tkrlist_l}
api.add_resource(Tkrs, '/tkrs')

class Istkr(fr.Resource):
  """
  This class should answer True, False given a tkr.
  """
  def get(self, tkr):
    torf = tkr in tkrlist_l
    return {'istkr': torf}
api.add_resource(Istkr, '/istkr/<tkr>')

class Years(fr.Resource):
  """
  This class should list all the years in years.txt
  """
  def get(self):
    return {'years': years_l}
api.add_resource(Years, '/years')

class Tkrprices(fr.Resource):
  """
  This class should list prices for a tkr.
  """
  def get(self, tkr):
    # I should get csvh from tkrprices in db:
    sql_s       = '''select csvh from tkrprices
      where tkr = %s  LIMIT 1'''
    result      = conn.execute(sql_s,[tkr])
    if not result.rowcount:
      return {'no': 'data found'}  
    myrow       = [row for row in result][0]
    return {'tkrprices': myrow.csvh.split()}
api.add_resource(Tkrprices, '/tkrprices/<tkr>')

def get_out_d(out_df):
  """This function should convert out_df to a readable format when in JSON."""
  out_l = []
  if out_df.empty :
    return {'sorry, no':'predictions'}
  for row in out_df.itertuples():
    row_d       = {
      'date,price':[row.cdate,row.cp]
      ,'pct_lead': row.pct_lead
      ,'prediction,effectiveness,accuracy':[row.prediction,row.effectiveness,row.accuracy]
    }
    out_l.append(row_d)
    lo_acc = sum((1+np.sign(out_df.pct_lead))/2) / out_df.accuracy.size
    out_d  = {'Long-Only-Accuracy': lo_acc }
    out_d['Long-Only-Effectivness'] = sum(out_df.pct_lead)
    out_d['Model-Effectivness']     = sum(out_df.effectiveness)
    out_d['Model-Accuracy']         = sum(out_df.accuracy) / out_df.accuracy.size
    out_d['Prediction-Count']       = out_df.prediction.size
    out_d['Prediction-Details']     = out_l
  return out_d

class Sklinear(fr.Resource):
  """
  This class should return predictions from sklearn.
  """
  def get(self, tkr,yrs,mnth,features):
    features_s = pgdb.check_features(features)
    out_df = sktkr.learn_predict_sklinear(tkr,yrs,mnth,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(Sklinear, '/sklinear/<tkr>/<int:yrs>/<mnth>/<features>')

class KerasLinear(fr.Resource):
  """
  This class should return predictions from keras.
  """
  def get(self, tkr,yrs,mnth,features):
    features_s = pgdb.check_features(features)
    out_df = kerastkr.learn_predict_keraslinear(tkr,yrs,mnth,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasLinear, '/keraslinear/<tkr>/<int:yrs>/<mnth>/<features>')
  
class KerasNN(fr.Resource):
  """
  This class should return predictions from keras.
  """
  def get(self, tkr,yrs,mnth):
    features0_s = fl.request.args.get('features', 'pct_lag1,slope3,dom')
    features_s = pgdb.check_features(features0_s)
    hl_s       = fl.request.args.get('hl', '2')      # default 2
    neurons_s  = fl.request.args.get('neurons', '4') # default 4
    hl_i       = int(hl_s)
    neurons_i  = int(neurons_s)
    out_df = kerastkr.learn_predict_kerasnn(tkr,yrs,mnth,features_s,hl_i,neurons_i)
    out_d      = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasNN, '/keras_nn/<tkr>/<int:yrs>/<mnth>')

class SklinearYr(fr.Resource):
  """
  This class should return predictions from sklearn for a Year.
  """
  def get(self, tkr,yrs,yr,features):
    features_s = pgdb.check_features(features)
    out_df = sktkr.learn_predict_sklinear_yr(tkr,yrs,yr,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(SklinearYr, '/sklinear_yr/<tkr>/<int:yrs>/<int:yr>/<features>')

class KeraslinearYr(fr.Resource):
  """
  This class should return predictions from keras for a Year.
  """
  def get(self, tkr,yrs,yr,features):
    features_s = pgdb.check_features(features)
    out_df = kerastkr.learn_predict_keraslinear_yr(tkr,yrs,yr,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KeraslinearYr, '/keraslinear_yr/<tkr>/<int:yrs>/<int:yr>/<features>')

class KerasNNYr(fr.Resource):
  """
  This class should return predictions from keras for a Year.
  """
  def get(self, tkr,yrs,yr):
    features0_s = fl.request.args.get('features', 'pct_lag1,slope3,dow')
    features_s = pgdb.check_features(features0_s)
    hl_s       = fl.request.args.get('hl', '2')      # default 2
    neurons_s  = fl.request.args.get('neurons', '4') # default 4
    hl_i       = int(hl_s)
    neurons_i  = int(neurons_s)
    out_df = kerastkr.learn_predict_kerasnn_yr(tkr,yrs,yr,features_s,hl_i,neurons_i)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasNNYr, '/keras_nn_yr/<tkr>/<int:yrs>/<int:yr>')

class SklinearTkr(fr.Resource):
  """
  This class should return all predictions from sklearn for a tkr.
  """
  def get(self, tkr,yrs,features):
    features_s = pgdb.check_features(features)
    out_df = sktkr.learn_predict_sklinear_tkr(tkr,yrs,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(SklinearTkr, '/sklinear_tkr/<tkr>/<int:yrs>/<features>')

class KeraslinearTkr(fr.Resource):
  """
  This class should return all predictions from keras for a tkr.
  """
  def get(self, tkr,yrs,features):
    features_s = pgdb.check_features(features)
    out_df = kerastkr.learn_predict_keraslinear_tkr(tkr,yrs,features_s)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KeraslinearTkr, '/keraslinear_tkr/<tkr>/<int:yrs>/<features>')

class KerasNNTkr(fr.Resource):
  """
  This class should return all predictions from keras for a tkr.
  """
  def get(self, tkr,yrs):
    features0_s = fl.request.args.get('features', 'pct_lag1,slope3,dow')
    features_s = pgdb.check_features(features0_s)
    hl_s       = fl.request.args.get('hl', '2')      # default 2
    neurons_s  = fl.request.args.get('neurons', '4') # default 4
    hl_i       = int(hl_s)
    neurons_i  = int(neurons_s)
    out_df = kerastkr.learn_predict_kerasnn_tkr(tkr,yrs,features_s,hl_i,neurons_i)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasNNTkr, '/keras_nn_tkr/<tkr>/<int:yrs>')
  
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  application.run(host='0.0.0.0', port=port)
'bye'
