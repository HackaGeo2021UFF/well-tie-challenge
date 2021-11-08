import json
import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np
import os

from src.waveletChoice import *
from src.seismicManipulation import *

def read_inputs(jpath):
    '''
            
    Arguments
        jpath: string
    Returns
        paths: dict
        
    '''
    with open(jpath) as file:
        paths = json.load(file)
    return paths

def read_data(ui):
    '''

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

    # read cube seismic

    # dado do desafio, usar somente no ambiente remoto
    #tr_seis, t_seis = seismic_trace = extract_seismic_trace(ui['well'], ui['seismic'])
    #t_seis = t_seis/1e3

    # dado de exemplo, pode usar na máquina pessoal
    df = pd.read_csv(ui['seismic'])
    tr_seis, t_seis = df.cdp409.to_numpy() , df.time.to_numpy()
    
    seismic = pd.DataFrame({'t':t_seis, 'tr_synth':np.zeros(len(tr_seis)), 'tr_seis':tr_seis})

    # read wavelet
    if ui['wavelet'] == "":
        wavelet = None
    else:    
        # wavelet = pd.read.csv(ui['wavelet']) 
        wavelet = None

    data = {'well':well,'seismic':seismic, 'wavelet':wavelet}
    return data

def pre_processing_data(data):
    
    data['well'].data['DT'] = np.nan_to_num(data['well'].data['DT'])
    #data['well'].data['RHOB'] = np.nan_to_num(data['well'].data['RHOB-EDIT'])
    data['well'].data['RHOB'] = np.nan_to_num(data['well'].data['RHOB'])


    #unit convert to µs/m
    data['well'].data['DT'] = data['well'].data['DT'] / 0.3048  
    #unit convert to kg/m3  
    #data['well'].data['RHOB'] = data['well'].data['RHOB-EDIT'] * 1000
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
    data['well'] = data['well'].df()
    return data

def time_depth_relationship(data):
    ### just an exemple
    ### TO DO: become smart
    log_start = data['well'].index[0]           # Depth of logging starts(m) from header
    kb = 29                                     # Kelly Bushing elevation(m) from header
    gap_int = log_start - kb
    v_water = 1500
    t_water_botton = 0.472
    log_start_time = t_water_botton + 2*(log_start - v_water*t_water_botton/2)*(np.array(data['well']['DT'])[0]/1e6) 

    #first replace NaN values with zero
    dt = data['well']['DT']
    dt_iterval = dt * 0.1524 / 1e6
    t_cum =  np.cumsum(dt_iterval) * 2
    data['well']['TWT'] = t_cum + log_start_time
    return data

def ai(data):
    # Sonic velocity calculate
    Vsonic = []
    for value in data['well']['DT_DS_SM']:
        if value == 0:
            Vsonic.append(0)
        else:
            Vsonic.append(1e6/value)

    data['well']['Vsonic'] = np.array(Vsonic)                                       #(unit: m/s)
    # AI calculate
    data['well']['AI'] = data['well']['Vsonic'] * data['well']['RHOB_DS_SM']        #(unit: kg/m2.s)
    return data

def rc_time(data):
    AI_tdom = np.interp(x=data['seismic']['t'].to_numpy(), xp = data['well'].TWT.to_numpy(), fp = data['well'].AI.to_numpy())    #resampling

    # again Rc calulation but in reampled time domain
    Rc_tdom = np.zeros(len(AI_tdom))
    for i in range(len(AI_tdom)-1):
        dem = AI_tdom[i]+AI_tdom[i+1]
        if dem == 0:
            Rc_tdom[i] = 0
        else:
            Rc_tdom[i] = (AI_tdom[i+1]-AI_tdom[i])/dem
    # to adjust vector size copy the last element to the tail
    Rc_tdom[-1] = Rc_tdom[-2]
    
    data['well_tdom'] = data['seismic']['t'].copy()
    data['well_tdom']['Rc_tdom'] = Rc_tdom
    data['well_tdom']['AI_tdom'] = AI_tdom

    return data

def synthetic_seismogram(data):

    if data['wavelet'] == None:
        cc, freq, roll = best_wavelet(data)
        w = ricker(freq,  data)
    else:
        w = data['wavelet']
        roll = 0
        cc = 0
        
    Rc_tdom = np.roll(data['well_tdom']['Rc_tdom'], roll)
    data['seismic']['tr_synth'] = np.convolve(w, Rc_tdom, mode='same')
    return data

def export_data(data, ui):
    
    if 'outputs' not in os.listdir():
        os.mkdir('outputs')

    with open('outputs/TD.dat','w') as file:
        file.write('SYN1 ' + ui['uwi_poco']   + '\n')
        file.write('SYN2 ' + ui['nome_poco']  + '\n')
        file.write('SYN3 ' + ui['nome_synth'] + '\n')
        file.write('SYN7 0 0 \n')

        time = data['well']['TWT'].to_numpy()
        depth = data['well'].index.to_numpy()
        n = len(data['well'])
        for i in range(n):
            file.write('SYN7 ' + str(time[i]) + ' ' + str(depth[i]) + '\n')

    data['seismic'].to_csv('outputs/synth.dat', index=False)
    
    return None
