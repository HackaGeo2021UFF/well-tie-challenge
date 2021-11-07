import json
import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np

from src.waveletChoice import *
from src.seismicManipulation import *

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

    # read cube seismic

    # dado do desafio, usar somente no ambiente remoto
    tr_seis, t_seis = seismic_trace = extract_seismic_trace(ui['well'], ui['seismic'])
    t_seis = t_seis/1e3

    # dado de exemplo, pode usar na máquina pessoal
    #df = pd.read_csv(ui['seismic'])
    #tr_seis, t_seis = np.array(df.cdp409), np.array(df.time)
    
    seismic = pd.DataFrame({'t':t_seis, 't_synth':np.zeros(len(tr_seis)), 'tr_seis':tr_seis})

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
    data['well'].data['RHOB-EDIT'] = np.nan_to_num(data['well'].data['RHOB-EDIT'])


    #unit convert to µs/m
    data['well'].data['DT'] = data['well'].data['DT'] / 0.3048  
    #unit convert to kg/m3  
    data['well'].data['RHOB'] = data['well'].data['RHOB-EDIT'] * 1000
    #data['well'].data['RHOB'] = data['well'].data['RHOB'] * 1000

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

    #repl_vel = (1500 + 2564)/2                  # this is from VSP data knowledge (m/s)
    #log_start_time = 2.0 * gap_int / repl_vel        # 2 for twt
    #print(log_start_time)

    #t_seis = data['seismic']['t_seis'].to_numpy()
    v_water = 1500
    t_water_botton = 0.472
    log_start_time = t_water_botton + 2*(log_start - v_water*t_water_botton/2)*(np.array(data['well']['DT'])[0]/1e6)
    #print(log_start_time)
    
    dt = data['well']['DT']

    #first replace NaN values with zero
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
    
    data['Rc_tdom'] = Rc_tdom # pd.Series(Rc_tdom, index= data['well'].index)
    data['AI_tdom'] = AI_tdom

    return data

def synthetic_seismogram(data):

    if data['wavelet'] == None:
        #wvlts = all_wavelet_and_cc(data)
        #w = find_best_wavelet(wvlts)
        maior_corr_final, melhor_freq, melhor_roll = best_wavelet(data)
    else:
        w = data['wavelet']
    
    #data['seismic']['tr_synth'] = np.convolve(w, data['Rc_tdom'], mode='same')
    
    w = make_ricker(melhor_freq)
    Rc_tdom = np.roll(data['Rc_tdom'], int(melhor_roll))
    #print(maior_corr_final)
    data['seismic']['tr_synth'] = np.convolve(w, Rc_tdom, mode='same')
    return data

def export_data(data):
    #df = pd.DataFrame(data['well'], columns=['amplitude'])
    #df.to_csv('outputs/well_tie.csv', index=False)
    #export TD.dat
    DT_pandas = data['well']['TWT'] # produto entregável
    DT_pandas.to_csv('DT_file.dat')

    #export Synth.dat
    
    Synth_pandas = data['seismic']['tr_synth'] # produto entregável
    Synth_pandas.to_csv('Synth_file.dat')

    #output_df = pd.data({'[column_name]': column_values})  
    #output_df.to_csv('output_file_name.dat')
    
    return None
