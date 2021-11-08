import numpy as np

def ricker(freq_hz):
    taxa_amostragem = 0.004
    tempo = np.arange(-0.3, 0.3, taxa_amostragem)
    freq_central = freq_hz * (2*np.pi)

    ricker = (1 - 0.5 * freq_central * freq_central * tempo * tempo) * \
        np.exp(-1/4 * freq_central * freq_central * tempo * tempo)
    return ricker

def band_pass():
    return np.zeros(1)

def evaluate_results(tr_synth, tr_seis):
    """
    Evaluate_results calculates the Pearson correlation coefficient between 
    two different seismic signals with different time coordinates

    Parameters
    ----------
    tr_synth : numpy.array
        The synthetic seismogram recovered from the well-tie process
    t_synth : numpy.array
        The time coordinates for the `tr_synth` signal
    tr_seis : numpy.array
        The seismic trace extracted from the seg-y file
    t_seis : numpy.array
        The time coordinates for the `amp_seis` signal

    Returns
    -------
    r: float
        The Pearson correlation coefficient R

    """    

    # amp_seis = amp_seis.mean(axis = 1)
    r = np.corrcoef(tr_synth, tr_seis)

    return r[0][1]

def matching(tr_seis, tr_synth):
    
    tr_seis_new = tr_seis.copy()

    i = 0
    while tr_synth[i] == 0 and i < len(tr_seis):
        tr_seis_new[i] = 0
        i += 1

    i = len(tr_seis)-1
    while tr_synth[i] != 0 and i >= 0:
        tr_seis_new[i] = 0
        i -= 1

    return tr_seis_new 

def best_wavelet(data):
    
    freqs = np.arange(5, 50+0.2, 0.2)
    corr_index = 0
    Rc_tdom = data['well_tdom']['Rc_tdom']

    for freq in freqs:

        wavelet = ricker(freq)
        tr_seis = data['seismic']['tr_seis'].to_numpy()
        tr_synth = np.convolve(wavelet, Rc_tdom, mode='same')
        
        for r in range(-10, 10):        #roll

            tr_synth_roll = np.roll(tr_synth, r)

            tr_seis_match = matching(tr_seis, tr_synth)
        
            corr = np.corrcoef(tr_synth_roll, tr_seis)[0][1]
            
            if corr > corr_index:
                best_corr = corr
                best_roll = r
                best_freq = freq
                corr_index = best_corr
    
    print("Best wavelet: f = %.2f, index roll = %i and corr = %.3f"%(best_freq, best_roll, best_corr))

    return best_corr, best_freq, int(best_roll)
