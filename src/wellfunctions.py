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

def twowaytime(log_start,kb,repl_vel,w):
    # Depth of logging starts(m) from header
    log_start = 1517.0          

    # Kelly Bushing elevation(m) from header
    kb = 15 
    # define the gap interval in m
    gap_int = log_start - kb


    # calculate the TWT for the gap
    log_start_time =  2 * gap_int / repl_vel # 2 for twt
    #log_start_time
    # replace NaN values with zero and convert DT to seconds to each interval
    dt_interval = np.nan_to_num(w.data['DT']) * 0.1524 / 1e6 #por que utiliza dt e não dt_ds_sm???????

    # now calculate the cumulative TWT starting at the 1st depth measured
    t_cum = np.cumsum(dt_interval) * 2

    # and now TWT for the whole depth range
    w.data['TWT'] = t_cum + log_start_time # por que mesmo que fazemos esta soma???????
    w.data['TWT'].values


def acoustic_imp(df):
    df['Vsonic'] = 1e6 / df['DT_DS_SM']
    df['AI'] = df['Vsonic'].values * df['RHOB_DS_SM'].values

def reflection_coefficient(df):
    ac_imp = df['AI'].values
    ref_coef = (ac_imp[1:] - ac_imp[:-1]) / (ac_imp[1:] + ac_imp[:-1])
    ref_coef = np.append(ref_coef, ref_coef[-1])
    df['REF_COEF'] = ref_coef

def acusticimpedancetimedomain(df):
    # define a sampling interval dt in s
    dt = 0.001

    # max time to create time vector in s
    t_max = 3.0   

    # create the new time vector to interpolate onto
    t = np.arange(0, t_max, dt)

    # and perform the interpolation/resampling
    AI_tdom = np.interp(x = t,
                        xp = df.TWT,
                        fp = df.AI)
    return AI_tdom 

def reflectivitycoeficienttimedomain(AI_tdom):
    # again Rc calulation but in resampled time domain
    Rc_tdom = []
    for i in range(len(AI_tdom) - 1):
        z = (AI_tdom[i+1] - AI_tdom[i]) / (AI_tdom[i+1] + AI_tdom[i])
        Rc_tdom.append(z)
        
    # to adjust vector size copy the last element to the tail
    Rc_tdom.append(Rc_tdom[-1])
    return  Rc_tdom
