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

df = w.df()

wf.acoustic_imp(df)

wf.reflection_coefficient(df)
