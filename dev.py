"""
dev.py

This script should help me do development.

Demo:
. env.bash
$PYTHON dev.py
"""

import codecs
import io
import pdb
import os
import flask
import datetime      as dt
import flask_restful as fr
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import keras
# modules in the py folder:

import pgdb
import kerastkr
import sktkr

out_df = kerastkr.load_predict_keraslinear()
print(out_df)

'bye'
