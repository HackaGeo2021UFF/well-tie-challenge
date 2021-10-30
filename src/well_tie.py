import json
from welly import Well
import pandas as pd

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

    data = {'well':well.data,'tops':tops_dict,'seismic':seismic_df}
    return data

def pre_processing_data(data):
    #unit convert to µs/m
    data['well']['DT'] = data['well']['DT'] / 0.3048  
    #unit convert to kg/m3  
    data['well']['RHOB'] = data['well']['RHOB'] * 1000

    #Despiking
    #Sonic Despiking
    dt = data['well']['DT']
    data['well']['DT_DS'] = dt.despike(window_length=50, z=2)

    #Density Despiking
    den = data['well']['RHOB']
    data['well']['RHOB_DS'] = den.despike(window_length=50, z=2)

    #Smoothing 
    #Sonic Smoothing
    dt_ds = data['well']['DT_DS']
    data['well']['DT_DS_SM'] = dt_ds.smooth(window_length=10, samples=False)

    #Density Smoothing
    den_ds = data['well']['RHOB_DS']
    data['well']['RHOB_DS_SM'] = den_ds.smooth(window_length=10, samples=False)
    return data

def time_depth_relationship(data, ):
    ### just an exemple
    ### TO DO: become it inteligence
    log_start = 1517               # Depth of logging starts(m) from header
    kb = 15                        # Kelly Bushing elevation(m) from header
    gap_int = log_start - kb
    repl_vel = 2632                # this is from VSP data knowledge (m/s)
    log_start_time = 2.0 * gap_int / repl_vel        # 2 for twt

    #first replace NaN values with zero
    dt_iterval = np.nan_to_num(dt) * 0.1524 / 1e6
    t_cum =  np.cumsum(dt_iterval) * 2
    w.data['TWT'] = t_cum + log_start_time
    return data

def rc_time(data):
    return data

def wvlt_conv(data):
    return data

def evaluate_results(data):
    return data

def export_data(data):
    return data