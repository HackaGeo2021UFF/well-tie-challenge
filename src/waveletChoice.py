import numpy as np

def ricker(f):
    length = 0.512
    dt = 0.004
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return y

def band_pass():
    return np.zeros(1)

def evaluate_results(tr_synth, t_synth, tr_seis, t_seis):
    """
    evaluate_results calculates the Pearson correlation coefficient between 
    two different seismic signals with different time coordinates

    Parameters
    ----------
    tr_synth : numpy.array
        The syntheticc seismogram recovered from the well-tie process
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
    
    # interpolate the synthetic seismogram onto the seismic trace time coordinates
    n_synth = np.interp(x=t_seis, xp = t_synth, fp = tr_synth)

    # amp_seis = amp_seis.mean(axis = 1)
    r = np.corrcoef(n_synth, tr_seis)

    return r[0][1]

def all_wavelet_and_cc(data):
    table = []

    wavelets = [ricker]
    
    indexs = np.arange(-30, 30, 1)
    n = len(indexs)
    freqs = np.linspace(2, 31, n)

    t_synth = data['seismic']['t']
    t_seis = data['seismic']['t']
    tr_seis = data['seismic']['tr_seis']

    i_min = None
    t_min = np.array(data['well']['TWT'])[0]
    for i in range(len(t_synth)):
        if t_synth[i] >= t_min and i_min == None:
            i_min = i
    
    i_max = None
    t_max = np.array(data['well']['TWT'])[-1]
    for i in range(len(t_synth)-1,-1,-1):
        if t_synth[i] <= t_max and i_max == None:
            i_max = i

    t_synth = t_synth[i_min:i_max]
    t_seis = t_seis[i_min:i_max]
    tr_seis = tr_seis[i_min:i_max]

    for iwvlt in wavelets:
        for ifreq in freqs:
            # convolution of the wavelet with `rc` to obtain
            w = iwvlt(ifreq)
            # the synthetic seismogram
            tr_synth = np.convolve(w, data['Rc_tdom'], mode='same')
            tr_synth = tr_synth[i_min:i_max]
            for iindex in indexs:
                # evaluate the recovered signal
                cc_score = evaluate_results(tr_synth, t_synth, tr_seis, t_seis) 
                table += [[cc_score, ifreq, iwvlt, iindex]]

    return table

def find_best_wavelet(wvlts):
    cc, freq, wvlt, dindex = sorted(wvlts, reverse=True)[0]
    w = wvlt(freq)
    print("Best wavelet: f = %.2f, dindex = %i and CC = %.2f"%(freq,dindex,cc))
    # TO DO: delta index
    return w
