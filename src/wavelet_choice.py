# define function of ricker wavelet
import numpy as np

def ricker(f):
    length = 1
    dt = 0.004
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return y

def outro_tipo_1(f):
    return np.zeros(1)

def outro_tipo_2(f):
    return np.zeros(1)

def evaluate_results(array1, array2, index):
    score = 1
    return score

def all_wavelet_and_cc(data):
    table = []

    wavelets = [ricker, outro_tipo_1, outro_tipo_2]
    
    indexs = np.arange(-30, 30, 1)
    n = len(indexs)
    freqs = np.linspace(5, 31, n)
        
    for iwvlt in wavelets:
        for ifreq in freqs:
            # convolution of the wavelet with `rc` to obtain
            w = iwvlt(ifreq)
            # the synthetic seismogram
            synthetic = np.convolve(w, data['Rc_tdom'], mode='same')
            for iindex in indexs:
                # evaluate the recovered signal
                cc_score = evaluate_results(synthetic, data, iindex) 
                table += [[str(iwvlt), ifreq, iindex, cc_score]]

    return np.matrix(table)

def find_best_wavelet(wvlts):
    return np.zeros(1)
