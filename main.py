'''
This file automates the well-tieing process

Usage is:

"python main.py inputs.json"

Arguments
    inputs.json: string
      the json file with its inputs
'''

import sys
import numpy as np

if __name__ == "__main__":

  # lib
  from src.well_tie import *

  # user inputs `ui` passed as a json file
  ui = read_inputs(sys.argv[1])

  # read data defined in the input file
  data = read_data(ui)

  # pre-processing of data
  data = pre_processing_data(data)

  # time-depth relationship `tdr` from DT
  data = time_depth_relationship(data)

  # acoustic impedance
  data = ai(data)

  # reflectivity coefficients `rc` profile (in time)
  data = rc_time(data)

  # inputs
  wavelets = ['ricker', 'outro_tipo_1', 'outro_tipo_2']
  freqs = np.linspace(5,31,5)
  times = np.linspace(-0.1,0.1,0.02)

  for iwvlt in wavelets:
    for ifreq in freqs:
      # convolution of the wavelet with `rc` to obtain
      wvlt = get_wavelet(iwvlt, ifreq)

      # the synthetic seismogram
      data = wvlt_conv(data, wvlt)

      for itimes in times:
        # evaluate the recovered signal
        score = evaluate_results(data) 

        # append to dataframe 
        # df.append()

  # export data to Decision Workspace
  export_data(data)
