'''Resampling to the time domain'''
''' Reflectivity series should be transferred into time domain for convolution. After defining the time vector, we can use the interpolation function from the numpy library'''

'''# download the data
import git
git.Git("/content").clone("https://github.com/mardani72/Synthetic_Seismogram.git")'''

###################################
# NEED AS IMPUT df.TWT and df.AI
###################################

import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np
#import Read_data as Rd
#import 'funçõesandersonAI'

w_path = 'Synthetic_Seismogram/KK1.las'
w = Well.from_las(w_path)

# runing with welly lib we are not able to see las header data
#print(w.header)

w_las= lasio.read(w_path) # lasio lib will help
#print(w_las.header)
w
def twowaytime(log_start,kb,repl_vel,w):
       
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

#AI_tdom = acusticimpedancetimedomain(TWT,AI)

def Reflectivitycoeficienttimedomain(AI_tdom):
    # again Rc calulation but in resampled time domain
    Rc_tdom = []
    for i in range(len(AI_tdom) - 1):
        z = (AI_tdom[i+1] - AI_tdom[i]) / (AI_tdom[i+1] + AI_tdom[i])
    Rc_tdom.append(z)
        
    # to adjust vector size copy the last element to the tail
    Rc_tdom.append(Rc_tdom[-1])
    return  Rc_tdom