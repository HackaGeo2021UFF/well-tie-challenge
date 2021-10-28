'''
This file automates the well-tieing process

Usage is:

"python grad_uff_solucao.py inputs.json"

Arguments
    inputs.json: string
      the json file with its inputs
'''

import welly
import las

# user inputs `ui` passed as a json file
ui = read_inputs(sys.argv[1])

# read data defined in the input file
data = read_data(ui)

# pre-processing of data
data = pre_processing_data(data)

# time-depth relationship `tdr` from DT
data = time_depth_relationship(data)

# reflectivity coefficients `rc` profile (in time)
data = rc_time(data)

# convolution of the wavelet with `rc` to obtain
# the synthetic seismogram
data = wvlt_conv(data)

# evaluate the recovered signal
score = evaluate_results(data)

# export data to Decision Workspace
export_data(data)