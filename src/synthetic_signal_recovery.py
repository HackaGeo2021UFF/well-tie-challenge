import numpy

# define function of ricker wavelet
def ricker(f, length, dt):
    t0 = np.arange(-length/2, (length-dt)/2, dt)
    y = (1.0 - 2.0*(np.pi**2)*(f**2)*(t0**2)) * np.exp(-(np.pi**2)*(f**2)*(t0**2))
    return t0, y

def convolution(Rc_tdom, f, length, dt):
    f=20            #wavelet frequency
    length=0.512    #Wavelet vector length
    dt=dt           # Sampling prefer to use smiliar to resampled AI
    t0, w = ricker (f, length, dt) # ricker wavelet 
    synthetic = np.convolve(w, Rc_tdom, mode='same')
    return synthetic
