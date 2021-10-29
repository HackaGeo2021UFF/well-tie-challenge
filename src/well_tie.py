import json
from welly import Well

def read_inputs(jpath):
    with open(jpath) as file:
        paths = json.load(file)
    return paths

def read_data(ui):
    '''
    Description
        
    Arguments
        path: string
    Returns
        well: welly.well.Well
    '''
    
    # read well .las
    well = Well.from_las(ui['well_path'])       

    # read from csv file into dataframe
    df_top = pd.read_csv(ui['tops'])            
    # convert to dictionary
    tops_dict = dict(df_top.values.tolist())    

    # read seismic arround well
    seismic_df = pd.read_csv(ui['seismic'])     

    data = {'well':well,'tops':tops_dict,'seismic':seismic_df}
    return data

def pre_processing_data(data):
    return None

def time_depth_relationship(data):
    return None

def rc_time(data):
    return None

def wvlt_conv(data):
    return None

def evaluate_results(data):
    return data

def export_data(data):
    return None