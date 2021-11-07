import numpy as np

def ricker(f):
    length = 0.512
    dt = 0.004
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return y

def band_pass():
    return np.zeros(1)

def evaluate_results(tr_synth, tr_seis):
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
    #n_synth = np.interp(x=t_seis, xp = t_synth, fp = tr_synth) #Essa interpolaço é necessária??

    # amp_seis = amp_seis.mean(axis = 1)
    r = np.corrcoef(tr_synth, tr_seis)

    return r[0][1]

def all_wavelet_and_cc(data):
    table = []

    wavelets = [ricker]
    
    indexs = np.arange(-30, 30, 1)
    n = len(indexs)
    freqs = np.linspace(2, 31, n)

    t_synth = data['seismic']['t']
    t_seis = data['seismic']['t'].to_numpy()
    tr_seis = data['seismic']['tr_seis'].to_numpy()

    #dt = (t_seis[1]-t_seis[0])*0.001  # precisa multiplicar mesmo?
    dt = (t_seis[1]-t_seis[0])
    
    Rc_tdom = data['Rc_tdom']
    
    for iwvlt in wavelets:
        for ifreq in freqs:
            # convolution of the wavelet with `rc` to obtain
            w = iwvlt(ifreq)
            # the synthetic seismogram
            tr_synth = np.convolve(w, Rc_tdom, mode='same')
            print(tr_synth)
            #tr_synth = tr_synth[i_min:i_max]
            for iindex in indexs:
                # evaluate the recovered signal
                #cc_score = evaluate_results(tr_synth, t_synth, tr_seis, t_seis) #
                cc_score = evaluate_results(tr_synth, tr_seis)
                table += [[cc_score, ifreq, iwvlt, iindex]]

    return table

def find_best_wavelet(wvlts):
    cc, freq, wvlt, dindex = sorted(wvlts, reverse=True)[0]
    w = wvlt(freq)
    print("Best wavelet: f = %.2f, dindex = %i and CC = %.2f"%(freq,dindex,cc))
    # TO DO: delta index
    return w
    
def make_ricker(freq):
    taxa_amostragem = 0.004
    tempo = np.arange(-0.3, 0.3, taxa_amostragem)
    freq_hz = freq
    freq_central = freq_hz * (2*np.pi)

    ricker = (1 - 0.5 * freq_central * freq_central * tempo * tempo) * \
        np.exp(-1/4 * freq_central * freq_central * tempo * tempo)
    return ricker

'''
def best_wavelet(data):
    Rc_tdom = data['Rc_tdom']
    seism_trace = data['seismic']['tr_seis'].to_numpy()

    
    maior_corr = 0
    freqs = np.arange(5, 30+0.2, 0.2)
    for j in range(len(freqs)):

        wavelet = make_ricker(freqs[j])

        synthetic = np.convolve(wavelet, Rc_tdom, mode='same')

        corr_index = 0
        roll = 0
        corr_roll = np.zeros([len(freqs),2])

        for i in range(-50, 50):
        
            synthetic_roll = np.roll(synthetic, i)
            corr_auxiliar = np.corrcoef(synthetic_roll, seism_trace)
            #print(corr_auxiliar)
            corr = corr_auxiliar[0][1]
            print(corr)
            
            if corr > corr_index:
                maior_corr = corr
                roll = i
            corr_index = corr
        
        corr_roll[j][0] = maior_corr
        corr_roll[j][1] = roll
    maior = -99
    for i in range(len(freqs)):
        if corr_roll[i][0] > maior:
            maior = corr_roll[i][0]
            index = i
    maior_corr_final = corr_roll[index][0]
    melhor_roll = corr_roll[index][1]
    melhor_freq = 5 + index*0.2
    return maior_corr_final, melhor_freq, melhor_roll
'''

def best_wavelet(data):
    freqs = np.arange(5, 50+0.2, 0.2)
    corr_index = 0
    for j in range(len(freqs)):

        wavelet = make_ricker(freqs[j])

        Rc_tdom = data['Rc_tdom']

        seism_trace = data['seismic']['tr_seis'].to_numpy()

        synthetic = np.convolve(wavelet, Rc_tdom, mode='same')

        for i in range(-10, 10):
            synthetic_roll = np.roll(synthetic, i)
            corr = np.corrcoef(synthetic_roll, seism_trace)[0][1]
            if corr > corr_index:
                maior_corr = corr
                melhor_roll = i
                melhor_freq = freqs[j]
                corr_index = maior_corr
    
    print("Best wavelet: f = %.2f, dindex = %i and CC = %.3f"%(melhor_freq,melhor_roll,maior_corr))

    return maior_corr, melhor_freq, int(melhor_roll)