import numpy as np

def ricker(f):
    length = 0.512
    dt = 0.004
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return y

def band_pass():
    return np.zeros(1)

def outro_tipo_1():
    return np.zeros(1)

def evaluate_results(synthetic, data, di):
    return 1

def all_wavelet_and_cc(data):
    table = []

    wavelets = [ricker]
    
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
                table += [[cc_score, ifreq, iwvlt, iindex]]

    return table

def find_best_wavelet(wvlts):
    cc, freq, wvlt, dindex = sorted(wvlts, reverse=True)[0]
    w = wvlt(freq)
    print("Best wavelet: f = %.2f, dindex = %i and CC = %.2f"%(freq,dindex,cc))
    # TO DO: delta index
    return w
