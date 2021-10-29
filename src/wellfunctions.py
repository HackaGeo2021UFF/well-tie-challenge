from typing import Type
from welly import Well
import pandas as pd
import lasio
import numpy as np
import matplotlib.pyplot as plt

# conversar sobre of inputs inicias e o type dos vetores
# UNIT CONVERSION
def conversion(w):
    w.data['DT'] = w.data['DT'] / 0.3048    # µs/ft to µs/m
    w.data['RHOB'] = w.data['RHOB'] * 1000  # unit convert to kg/m3

def despike_smoothing(w):
    w.data['DT_DS'] = w.data['DT'].despike(window_length=50, z=2)
    w.data['RHOB_DS'] = w.data['RHOB'].despike(window_length=50, z=2)

    w.data['DT_DS_SM'] = w.data['DT_DS'].smooth(
        window_length=10, samples=False)
    w.data['RHOB_DS_SM'] = w.data['RHOB_DS'].smooth(
        window_length=10, samples=False)

def acoustic_imp(df):
    df['Vsonic'] = 1e6 / df['DT_DS_SM']
    df['AC_IMP'] = df['Vsonic'].values * df['RHOB_DS_SM'].values

def reflection_coefficient(df):
    ac_imp = df['AC_IMP'].values
    ref_coef = (ac_imp[1:] - ac_imp[:-1]) / (ac_imp[1:] + ac_imp[:-1])
    ref_coef = np.append(ref_coef, ref_coef[-1])
    df['REF_COEF'] = ref_coef


