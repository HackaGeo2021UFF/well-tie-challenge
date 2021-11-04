from os import path
from src import read_data as rd
from src import wellfunctions as wf
from typing import Type
from welly import Well
import pandas as pd
import lasio
import numpy as np
import matplotlib.pyplot as plt

# download the data
import git
#git.Git("/content").clone("https://github.com/mardani72/Synthetic_Seismogram.git")

#setting the path and reading data
w_path = 'Synthetic_Seismogram/KK1.las'
w = rd.read_las(w_path)

#
wf.despike_smoothing(w)

# Depth of logging starts(m) from header
log_start = 1517.0   
# Kelly Bushing elevation(m) from header
kb = 15 
# define the gap velocity
repl_vel = 2632                # this is from VSP data knowledge (m/s)

wf.twowaytime(log_start,kb,repl_vel,w)

df = w.df()

wf.acoustic_imp(df)

wf.reflection_coefficient(df)

wf.reflectivitycoeficienttimedomain(wf.acusticimpedancetimedomain(df))