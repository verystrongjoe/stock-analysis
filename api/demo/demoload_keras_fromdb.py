"""
demoload_keras_fromdb.py

This script should demonstrate how to load a keras model from db and use it to predict.

Demo:
. ../env.bash
~/anaconda3/bin/python demoload_keras_fromdb

"""

import api.kerastkr as kerastkr

out_df = kerastkr.load_predict_keraslinear()
print(out_df)

'bye'
