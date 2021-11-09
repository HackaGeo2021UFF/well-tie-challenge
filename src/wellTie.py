import json
import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np
import os
import matplotlib.pyplot as plt

from src.waveletChoice import *
from src.seismicManipulation import *

def read_inputs(jpath):
    """
    read_inputs reads the input json file and stores it information in a dictionary

    Parameters
    ----------
    jpath : string
        the input JSON file

    Returns
    -------
    paths: dict
        Returns a dictionary of the json file

    """
    with open(jpath) as file:
        paths = json.load(file)
    return paths

def read_data(ui):
    """
    read_data reads the input data and stores it in a dictionary

    Parameters
    ----------
    ui: dict
        A dictionary of the user inputs

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
    
    # read well .las
    well = Well.from_las(ui['well'])
    ui['uwi'] = well.header['uwi']
    ui['well_name'] = well.header['name']

    # read cube seismic

    # dado do desafio, usar somente no ambiente remoto
    tr_seis, t_seis = seismic_trace = extract_seismic_trace(ui['well'], ui['seismic'])
    t_seis = t_seis/1e3

    # dado de exemplo, pode usar na máquina pessoal
    #df = pd.read_csv(ui['seismic'])
    #tr_seis, t_seis = df.cdp409.to_numpy() , df.time.to_numpy()
    
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
    """
    pre_processing_data pre-process the well DT and RHOB data with operations as:
    * despike
    * smooth

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
    
    data['well'].data['DT'] = np.nan_to_num(data['well'].data['DT'])
    data['well'].data['RHOB'] = np.nan_to_num(data['well'].data['RHOB-EDIT'])
    #data['well'].data['RHOB'] = np.nan_to_num(data['well'].data['RHOB'])


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

def time_depth_relationship(data, ui):
    """
    time_depth_relationship creates the time-depth relationship from the sonic (DT) log

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    ui: dict
        Returns a dictionary of the user inputs

    """
    ### just an exemple
    ### TO DO: become smart
    log_start = data['well'].index[0]           # Depth of logging starts(m) from header
    kb = ui['kb']                               # Kelly Bushing elevation(m) from header
    gap_int = log_start - kb
    v_water = 1500
    t_water_botton = ui['t_water_botton']
    log_start_time = t_water_botton + 2*(log_start - v_water*t_water_botton/2)*(np.array(data['well']['DT'])[0]/1e6) 

    #first replace NaN values with zero
    dt = data['well']['DT']
    dt_iterval = dt * 0.1524 / 1e6
    t_cum =  np.cumsum(dt_iterval) * 2
    data['well']['TWT'] = t_cum + log_start_time
    return data

def ai(data):
    """
    ai creates the accoustic impedance log

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
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
    """
    rc_time creates the Reflectivity Coefficients log in the time-domain

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
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
    
    i = 0
    while Rc_tdom[i] == 0 and i < len(Rc_tdom):
        i += 1
    Rc_tdom[i] = Rc_tdom[i+1]

    i = len(Rc_tdom)-1
    while Rc_tdom[i] == 0 and i > 0:
        i -= 1
    Rc_tdom[i] = Rc_tdom[i-1]
    
    data['well_tdom'] = pd.DataFrame()
    data['well_tdom']['t'] = data['seismic']['t']
    data['well_tdom']['Rc_tdom'] = Rc_tdom
    data['well_tdom']['AI_tdom'] = AI_tdom

    return data

def synthetic_seismogram(data):
    """
    synthetic_seismogram creates the synthetic seismogram

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """

    if data['wavelet'] == None:
        cc, freq, roll, phase = best_wavelet(data)
        w = ricker(freq, phase, data)
    else:
        w = data['wavelet']
        
    Rc_tdom = np.roll(data['well_tdom']['Rc_tdom'], roll)
    data['seismic']['tr_synth'] = np.convolve(w, Rc_tdom, mode='same')
    return data

def normalization(data):
    """
    normalization normalizes the synthetic and seismic signals

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
    data['seismic']['tr_synth'] = data['seismic']['tr_synth']/np.max(data['seismic']['tr_synth'])
    data['seismic']['tr_seis'] = data['seismic']['tr_seis']/np.max(data['seismic']['tr_seis'])
    return data

def export_data(data, ui):
    """
    export_data exports data in the Decision Workspace format

    Parameters
    ----------
    data: dict
        A dictionary containing all the data that will be used throughout the code
    ui: dict
        A dictionary of the user inputs 

    Returns
    -------
    data: dict
        Returns a dictionary containing all the data that will be used throughout the code

    """
    
    if 'outputs' not in os.listdir():
        os.mkdir('outputs')

    result_path = ui['well_name'].strip().replace("/","_")

    twt = data['well']['TWT'].to_numpy()*1000
    twt = np.insert(twt, 0, 0)
    depth = data['well'].index.to_numpy()
    depth = np.insert(depth, 0, 0)

    t = data['seismic']['t'].to_numpy()*1000
    new_depth = np.interp(t,twt,depth)
    amp = data['seismic']['tr_synth'].to_numpy()

    with open('outputs/'+result_path+'_TD.dat','w') as file:
        file.write('TDP1     '+ ui['uwi']   + '\n')
        file.write('TDP2          ' + ui['well_name']  + '\n')
        
        line = 'TDP3            ' + ui['td_name'] + ' '*70
        line = line[:73]
        line += ' 0             TVDBTDD\n'
        file.write(line)
      
        n = len(t)
        for i in range(n):
            line = 'TDP5   %.6f      '%t[i]
            line = line[:21] 
            line += '%.5f\n'%new_depth[i]
            file.write(line)
  
    with open('outputs/'+result_path+'_synth.dat','w') as file:
        file.write('SYN1       '+ ui['uwi']   + '\n')
        file.write('SYN2          ' + ui['well_name']  + '\n')

        line = 'SYN3                    ' + ui['synth_name'] + ' '*30
        line = line[:70]
        line += '4.0\n'
        file.write(line)
        
        
        n = len(t)
        for i in range(n):
            line = 'SYN7            %.6f           '%t[i]
            line = line[:28] 
            line += '%.6f\n'%amp[i]
            file.write(line)

    return None
