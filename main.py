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
  from src.wellTie import *

  # user inputs `ui` passed as a json file
  if len(sys.argv) == 1:
        path = "data/inputs_hackageo.json"
  else:
        path = sys.argv[1]
  ui = read_inputs(path)

  # read data defined in the input file
  data = read_data(ui)

  # pre-processing of data
  data = pre_processing_data(data)

  # time-depth relationship `tdr` from DT
  data = time_depth_relationship(data, ui)

  # acoustic impedance
  data = ai(data)

  # reflectivity coefficients `rc` profile (in time)
  data = rc_time(data)

  # convolution of the wavelet with `rc` to obtain the synthetic seismogram
  data = synthetic_seismogram(data)

  data = normalization(data)

  # export data to Decision Workspace
  export_data(data, ui)
