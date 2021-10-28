'''Esse é apenas um '.py' teste.'''

import numpy as np
import matplotlib.pyplot as plt

x= np.arange(0,10,0.1)
y = np.exp(x)

print(y)

#plt.figure(figsize=(5,5))
plt.plot(x,y)
plt.show()