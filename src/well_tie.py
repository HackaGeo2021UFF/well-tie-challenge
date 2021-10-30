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
    ### TO DO: become smart
    log_start = 1517               # Depth of logging starts(m) from header
    kb = 15                        # Kelly Bushing elevation(m) from header
    gap_int = log_start - kb
    repl_vel = 2632                # this is from VSP data knowledge (m/s)
    log_start_time = 2.0 * gap_int / repl_vel        # 2 for twt

    #first replace NaN values with zero
    dt_iterval = np.nan_to_num(dt) * 0.1524 / 1e6
    t_cum =  np.cumsum(dt_iterval) * 2
    data['well']['TWT'] = t_cum + log_start_time
    data['well'] = data['well'].df()
    return data

def ia(data):
    # Sonic velocity calculate
    data['well']['Vsonic'] = 1e6/df.DT_DS_SM                    #(unit: m/s)
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
    data['well']['Rc'] = pd.Series(Rc, index=df.index)

    dt = 0.001   #sampleing interval
    t_max = 3.0   # max time to create time vector
    t = np.arange(0, t_max, dt)
    AI_tdom = np.interp(x=t, xp = df.TWT, fp = df.AI)    #resampling

    # again Rc calulation but in reampled time domain
    Rc_tdom = []
    for i in range(len(AI_tdom)-1):
        Rc_tdom.append((AI_tdom[i+1]-AI_tdom[i])/(AI_tdom[i]+AI_tdom[i+1]))
    # to adjust vector size copy the last element to the tail
    Rc_tdom.append(Rc_tdom[-1])
    data['well']['Rc_tdom'] = pd.Series(Rc_tdom, index=df.index)

    return data

# define function of ricker wavelet
def ricker(f, length, dt):
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return t0, y

def wvlt_conv(data):
    # TO DO: become smart
    f=20            #wavelet frequency
    length=0.512    #Wavelet vector length
    dt=0.001        # Sampling prefer to use smiliar to resampled AI
    
    t0, w = ricker (f, length, dt) # ricker wavelet 
    synthetic = np.convolve(w, Rc_tdom, mode='same')

    data['synthetic seismogram'] = synthetic
    return data

def evaluate_results(data):
    score = []
    return score

def export_data(data):
    return None