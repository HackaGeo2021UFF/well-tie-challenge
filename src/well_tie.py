import json
import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np

from src.wavelet_choice import *

def read_inputs(jpath):
    with open(jpath) as file:
        paths = json.load(file)
    return paths

def read_data(ui):
    '''
    Description
        
    Arguments
        ui: dict with string
    Returns
        data: dict
        Description
            Well: welly.well.Well
            Tops: dataframe
            Seismic: dataframe
    '''
    
    # read well .las
    well = Well.from_las(ui['well'])       

    # read from csv file into dataframe
    df_top = pd.read_csv(ui['tops'])            
    # convert to dictionary
    tops_dict = dict(df_top.values.tolist())    

    # read seismic arround well
    seismic_df = pd.read_csv(ui['seismic']) 

    # read wavelet
    if ui['wavelet'] == "":
        wavelet = None
    else:    
        # wavelet = pd.read.csv(ui['wavelet']) 
        wavelet = None

    data = {'well':well,'tops':tops_dict,'seismic':seismic_df, 'wavelet':wavelet}
    return data

def pre_processing_data(data):
    #unit convert to µs/m
    data['well'].data['DT'] = data['well'].data['DT'] / 0.3048  
    #unit convert to kg/m3  
    data['well'].data['RHOB'] = data['well'].data['RHOB'] * 1000

    #Despiking
    #Sonic Despiking
    dt = data['well'].data['DT']
    data['well'].data['DT_DS'] = dt.despike(window_length=50, z=2)

    #Density Despiking
    den = data['well'].data['RHOB']
    data['well'].data['RHOB_DS'] = den.despike(window_length=50, z=2)

    #Smoothing 
    #Sonic Smoothing
    dt_ds = data['well'].data['DT_DS']
    data['well'].data['DT_DS_SM'] = dt_ds.smooth(window_length=10, samples=False)

    #Density Smoothing
    den_ds = data['well'].data['RHOB_DS']
    data['well'].data['RHOB_DS_SM'] = den_ds.smooth(window_length=10, samples=False)
    return data

def time_depth_relationship(data):
    ### just an exemple
    ### TO DO: become smart
    log_start = 1517               # Depth of logging starts(m) from header
    kb = 15                        # Kelly Bushing elevation(m) from header
    gap_int = log_start - kb
    repl_vel = 2632                # this is from VSP data knowledge (m/s)
    log_start_time = 2.0 * gap_int / repl_vel        # 2 for twt
    dt = data['well'].data['DT']

    #first replace NaN values with zero
    dt_iterval = np.nan_to_num(dt) * 0.1524 / 1e6
    t_cum =  np.cumsum(dt_iterval) * 2
    data['well'].data['TWT'] = t_cum + log_start_time
    data['well'] = data['well'].df()
    return data

def ai(data):
    # Sonic velocity calculate
    data['well']['Vsonic'] = 1e6/data['well']['DT_DS_SM']                    #(unit: m/s)
    # AI calculate
    data['well']['AI'] = data['well']['Vsonic'] * data['well']['RHOB_DS_SM']        #(unit: kg/m2.s)
    return data

def rc_time(data):
    Imp = data['well']['AI'].values
    Rc=[]
    for i in range(len(Imp)-1):
        Rc.append((Imp[i+1]-Imp[i])/(Imp[i]+Imp[i+1]))
    # to adjust vector size copy the last element to the tail
    Rc.append(Rc[-1])
    # Let's add Rc into dataframe as new column
    data['well']['Rc'] = pd.Series(Rc, index=data['well'].index)

    dt = 0.004   #sampleing interval
    t_max = 5.5   # max time to create time vector
    t = np.arange(0, t_max+dt, dt)
    AI_tdom = np.interp(x=t, xp = data['well'].TWT, fp = data['well'].AI)    #resampling

    # again Rc calulation but in reampled time domain
    Rc_tdom = []
    for i in range(len(AI_tdom)-1):
        Rc_tdom.append((AI_tdom[i+1]-AI_tdom[i])/(AI_tdom[i]+AI_tdom[i+1]))
    # to adjust vector size copy the last element to the tail
    Rc_tdom.append(Rc_tdom[-1])
    data['Rc_tdom'] = Rc_tdom # pd.Series(Rc_tdom, index= data['well'].index)

    return data

def synthetic_seismogram(data):

    if data['wavelet'] == None:
        data['wavelet_analysis'] = all_wavelet_and_cc(data)
        w = find_best_wavelet(data['wavelet_analysis'])
    else:
        w = data['wavelet']
    
    data['synthetic seismogram'] = np.convolve(w, data['Rc_tdom'], mode='same')

    return data

def export_data(data):
    return None
