import welly
from welly import Well
import pandas as pd
import lasio
import numpy as np
import xarray as xr

from segysak.segy import segy_header_scan, segy_header_scrape, get_segy_texthead, segy_loader

# function to find closest trace
def closest_trace(well_pos, seismic_traces_pos, n_traces_to_stack):
    """
    closest_trace finds the closest `n_traces_to_stack` traces in `seismic_traces_pos` to `well_pos`

    Parameters
    ----------
    well_pos : numpy.array
        A np.array([x,y]) with the `x` and `y` projected coordinates. 
        shape = (2,)
    seismic_traces_pos : numpy.array
        A np.array([x,y]) with the `x` and `y` projected coordinates
        shape = (2,n)

    Returns
    -------
    np.argmin(dist_2): int
        Returns the index that contains the closest trace to `well_pos` in `seismic_traces_pos`

    """
    seismic_traces_pos = np.asarray(seismic_traces_pos)
    dist_2 = np.sum((seismic_traces_pos - well_pos)**2, axis=1)
    return np.argpartition(dist_2, n_traces_to_stack)[:n_traces_to_stack]
    # return np.argmin(dist_2)

def extract_seismic_trace(well_file, segy_file):
    """
    extract_seismic_trace extracts the closest trace in `segy_file` to `well_file`

    Parameters
    ----------
    well_file : string
        The path to the well file
    segy_file : string
        The path to the seg-y file

    Returns
    -------
    seisnc_around_well.values: numpy.array
        An array with the amplitude values with the `t` time coordinates
    t: numpy.array
        An array with the time coordinates    

    """    

    # well filepath
    # w_path = '6507_8-1_DT_RHOB.LAS'
    w_path = well_file

    # load well data with welly
    w = Well.from_las(w_path)

    # lasio lib will help with header
    w_las = lasio.read(w_path) 

    # well location (projected coordinates)
    w_x = w_las.header['Well']['XCOORD']['value']
    w_y = w_las.header['Well']['YCOORD']['value']

    # check if segy file exists
    # segy_file = pathlib.Path("full_offset-cmp_02.sgy") 

    # read all trace headers
    trace_headers = segy_header_scrape(segy_file)

    # define location of all seismic traces
    seismic_trace_loc = np.array([trace_headers.CDP_X.values/100,
                                    trace_headers.CDP_Y.values/100])

    # the well location
    well_loc = np.array([w_x, w_y])

    # find the closest traces
    # TODO remove n_traces_to_stack 
    n_traces_to_stack = 4
    idx = closest_trace(well_loc, seismic_trace_loc.T, n_traces_to_stack)

    # extract closest traces
    seisnc_around_well = segy_loader(
        segy_file,
        head_df=trace_headers.iloc[idx].copy()
    )

    # extract time
    t = seisnc_around_well.twt.values
    
    # stack the seismic traces
    amplitude = seisnc_around_well.data.values.reshape(n_traces_to_stack,
                                                       seisnc_around_well.data.shape[-1]).mean(axis=0)

    return amplitude, t
