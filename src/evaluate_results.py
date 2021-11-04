import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np
import xarray as xr

from segysak.segy import segy_header_scan, segy_header_scrape, get_segy_texthead, segy_loader

# function to find closest trace
def closest_trace(well_pos, seismic_traces_pos):
    seismic_traces_pos = np.asarray(seismic_traces_pos)
    dist_2 = np.sum((seismic_traces_pos - well_pos)**2, axis=1)
    return np.argmin(dist_2)

def extract_seismic_trace(well_file, segy_file):

    # well filepath
    # w_path = '6507_8-1_DT_RHOB.LAS'
    w_path = well_file

    # load well data with welly
    w = Well.from_las(w_path)

    # lasio lib will help with header
    w_las = lasio.read(w_path) 
    w_las.header

    # well location (projected coordinates)
    w_x = w_las.header['Well']['XCOORD']['value']
    w_y = w_las.header['Well']['YCOORD']['value']
    # print(w_x, w_y)

    # check if segy file exists
    # segy_file = pathlib.Path("full_offset-cmp_02.sgy") # colab online
    # print("SEG-Y exists:", segy_file.exists())

    # read all trace headers
    trace_headers = segy_header_scrape(segy_file)

    # define location of all seismic traces
    seismic_trace_loc = np.array([trace_headers.CDP_X.values/100,
                                    trace_headers.CDP_Y.values/100])

    # the well location
    well_loc = np.array([w_x, w_y])

    # find the closest trace
    idx = closest_trace(well_loc, seismic_trace_loc.T)

    # extract closest trace
    seisnc_aropund_well = segy_loader(
        segy_file,
        head_df=trace_headers.iloc[[idx]].copy()
    )

    # extract time
    t = seisnc_aropund_well.twt.values

    return seisnc_aropund_well.values, t

def evaluate_results(synth_seism, t_synth, seis_tr, t_seis_tr):
    
    n_synthetic = np.interp(x=t_seis_tr, xp = t_synth, fp = synth_seism)

    # seis_tr = seis_tr.mean(axis = 1)
    r = np.corrcoef(n_synthetic,seis_tr)

    return r