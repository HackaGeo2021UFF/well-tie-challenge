import numpy as np
from scipy import signal

def ricker(freq_hz, phase, data):
    """
    ricker calculates the ricker wavelet

    Parameters
    ----------
    freq_hz : float
        the wavelet frequency
    phase : float
        The wavelet phase in degrees
    data : dict
        A dictionary that carries all the data

    Returns
    -------
    ricker: numpy.array
        Returns the complex riicker wavelet amplitude

    """
    t = data['seismic']['t']
    dt = t[1] - t[0]
    tempo = np.arange(-0.3, 0.3, dt)
    freq_central = freq_hz * (2*np.pi)

    ricker = (1 - 0.5 * freq_central * freq_central * tempo * tempo) * \
        np.exp(-1/4 * freq_central * freq_central * tempo * tempo)
    ricker = np.real(np.exp(1j*np.radians(phase)) * signal.hilbert(ricker))
    return ricker

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

def matching(tr_synth, tr_seis):
    """
    matching zeroes all values of the seismic trace `tr_seis` 
    outside the limits of the synthetic trace `tr_synth`

    Parameters
    ----------
    tr_synth : numpy.array
        The synthetic trace
    tr_seis : numpy.array
        The seismic trace

    Returns
    -------
    tr_seis_new: numpy.array
        Returns the new seismic trace (with zeros outside the area of comparison)

    """
    tr_seis_new = tr_seis.copy()
    i = 0
    while tr_synth[i] == 0 and i < len(tr_seis):
        tr_seis_new[i] = 0
        i += 1
    i = len(tr_seis)-1
    while tr_synth[i] == 0 and i >= 0:
        tr_seis_new[i] = 0
        i -= 1
    return tr_seis_new 

def best_wavelet(data):
    """
    best_wavelet calculates the best wavelet for the well-tie calculus based on the Pearson Correlation Coefficient R.
    This calculus iterates over:
    * a frequency range
    * a phase range
    * some wavelet types
    * a signal-translation range

    Parameters
    ----------
    data : dict
        The dictionary with all the data
        
    Returns
    -------
    best_corr: float
        The value of the correlation coefficient of the best choice
    best_freq: float
        The frequency of the best choice
    best_phase: float
        The phase of the best choice
    best_roll: float
        The signal rolling that yielded the best choice

    """
    
    phases = np.arange(0,180,10)
    freqs = np.arange(5, 50+0.2, 0.5)
    rolls = np.arange(-10,10,1)
    tr_seis = data['seismic']['tr_seis'].to_numpy()
    Rc_tdom = data['well_tdom']['Rc_tdom']
    best_corr = None
    
    for freq in freqs:
        for phase in phases:
            wavelet = ricker(freq, phase, data)
            tr_synth = np.convolve(wavelet, Rc_tdom, mode='same')            
            for r in rolls:
                tr_synth_roll = np.roll(tr_synth, r)
                tr_seis_match = matching(tr_synth, tr_seis)
                corr = evaluate_results(tr_synth_roll, tr_seis_match)
                
                if best_corr == None:
                    best_corr = corr
                    best_roll = r
                    best_freq = freq
                elif corr > best_corr:
                    best_corr = corr
                    best_roll = r
                    best_freq = freq
                    best_phase = phase
    
    print("Best wavelet: f = %.2f, index roll = %i, corr = %.3f and best phase = %i"%(best_freq, best_roll, best_corr, best_phase))

    return best_corr, best_freq, best_phase, best_roll
