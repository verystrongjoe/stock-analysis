"""
demokeras.py

This script should demo keras.

Demo:
. ../env.bash
~/anaconda3/bin/python demokeras.py
"""

import io
import keras
import pdb
import os
import numpy      as np
import sqlalchemy as sql

x_a = np.array(
[[  1.1,  2.2]
 ,[ 2.1,  3.2]
 ,[ 3.1,  4.2]
 ,[ 4.1,  5.2]
 ,[ 5.1,  6.2]])

y_a = np.array(
[[  1.3]
 ,[ 2.1]
 ,[ 3.4]
 ,[ 4. ]
 ,[ 5.2]])

print('x_a:')
print(x_a)
print(x_a.shape)
print('y_a:')
print(y_a)
print(y_a.shape)

# I should build a keras model.
# https://keras.io/models/sequential/#the-sequential-model-api
kmodel     = keras.models.Sequential()

# https://keras.io/getting-started/sequential-model-guide/#specifying-the-input-shape
features_i = len(x_a[0])
kmodel.add(keras.layers.core.Dense(features_i, input_shape=(features_i,)))

# https://keras.io/activations/
kmodel.add(keras.layers.core.Activation('linear'))
# I should have 1 linear-output:
kmodel.add(keras.layers.core.Dense(1)) 
kmodel.add(keras.layers.core.Activation('linear'))
kmodel.compile(loss='mean_squared_error', optimizer='adam')
kmodel.fit(x_a,y_a, batch_size=4, epochs=128)
xtest_a      = np.array([2.4,3.6]).reshape(1,2) # 1 row, 2 columns
prediction_a = kmodel.predict(xtest_a) # s.b. about 2.5

print('prediction_a:')
print( prediction_a)

# I should save the model:
kmodel.save('/tmp/kmodel.h5')

# I should create a new model from the h5-file:
kmodel2       = keras.models.load_model('/tmp/kmodel.h5')

# I should use it to predict again:
prediction2_a = kmodel2.predict(xtest_a) # s.b. about 2.5

print('prediction2_a:')
print( prediction2_a)

# I should save the model to the db:
db_s = 'postgres://tkrapi:tkrapi@127.0.0.1/tkrapi'
conn = sql.create_engine(db_s).connect()

sql_s = 'drop table if exists demokeras'
conn.execute(sql_s)

sql_s = 'create table if not exists demokeras(kmodel bytea)'
conn.execute(sql_s)

with open('/tmp/kmodel.h5','rb') as fh:
    kmodel3 = fh.read()

# I should copy the file into the db
sql_s = 'insert into demokeras(kmodel)values( %s )'
conn.execute(sql_s,[kmodel3])

# In psql I should run this to check my work:
# select count(*) from demokeras;

# I should copy bytes out of the bytea column into Python:
sql_s   = 'select kmodel from demokeras limit 1'
result  = conn.execute(sql_s)
myrow   = [row for row in result][0]
# https://docs.python.org/3/library/functions.html
kmodel4 = bytes(myrow.kmodel)

# I should write the bytes to a file:
with open('/tmp/kmodel4.h5','wb') as fh:
    fh.write(kmodel4)

# I should create a new model from the h5-file:
kmodel5 = keras.models.load_model('/tmp/kmodel4.h5')

# I should use it to predict again:
prediction3_a = kmodel5.predict(xtest_a) # s.b. about 2.5

print('prediction3_a:')
print( prediction3_a)

'bye'
