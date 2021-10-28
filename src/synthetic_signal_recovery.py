import numpy

# define function of ricker wavelet
def ricker(f, length, dt):
      '''
    Description
        The Ricker wavelet is a model seismic wavelet, sometimes called a Mexican hat wavelet (https://subsurfwiki.org/wiki/Ricker_wavelet)
    Arguments
        f: float
            Description: wavelet frequency
        length: float
            Description: Wavelet vector length
        dt: float
            Description: Sampling prefer to use smiliar to resampled AI
    Returns
        t0: array
        y: array
  '''
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return t0, y

def convolution(Rc_tdom, f, length, dt):
    '''
    Description
        Convolution to recover synthetic signal
    Arguments
        Rc_tdom: array
            Description: Reflection Coefficient
        f: float
            Description: wavelet frequency
        length: float
            Description: Wavelet vector length
        dt: float
            Description: Sampling prefer to use smiliar to resampled AI
    Returns
        t0: array
        y: array
    '''
    t0, w = ricker (f, length, dt) # ricker wavelet 
    synthetic = np.convolve(w, Rc_tdom, mode='same')
    return synthetic
