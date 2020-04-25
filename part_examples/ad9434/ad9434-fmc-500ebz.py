'''
AD9434-FMC-500EBZ super simple data capture example
Tested on ZC706 board.

'''

import sys

try: 
    import iio
except:
    print ("iio not found!")
    sys.exit(0)

import time, struct
import numpy as np
import matplotlib.pyplot as plt

bufflen = 8192

# Setup Context
my_ip = 'ip:192.168.2.1' # Pluto's default
my_ip = 'ip:10.54.6.12' # Change to command-line argument
try:
    ctx = iio.Context(my_ip)
except:
    print("No device found")
    sys.exit(0)    

clock = ctx.find_device("ad9571-4")
rxadc = ctx.find_device("axi-ad9434-core-lpc") # RX/ADC Core in HDL for DMA

v0 = rxadc.find_channel("voltage0")
v0.enabled = True
rxbuf = iio.Buffer(rxadc, bufflen, False) # False = non-cyclic buffer

for j in range(5): #Flush buffers.
    rxbuf.refill()
    x = rxbuf.read()

# got our data, clean up...
del rxbuf
del ctx
          
#get data from buffer
data = np.frombuffer(x, np.int16)

adc_amplitude = 2**12

window = np.blackman(bufflen) / sum(np.blackman(bufflen)) # Windown funciton, normalized to unity gain
data_nodc = data - np.average(data)
windowed_data = window * data_nodc
freq_domain = np.fft.fft(windowed_data)/(bufflen) # FFT
freq_domain_magnitude = np.abs(freq_domain) # Extract magnitude
freq_domain_magnitude *= 2 
freq_domain_magnitude_db = 20 * np.log10(freq_domain_magnitude/adc_amplitude)



plt.figure(1)
plt.clf()
plt.subplot(2,1,1)
fig = plt.gcf()
fig.subplots_adjust(right=0.68)
plt.plot(data)
plt.title('Ch0: Time Domain Samples')

plt.subplot(2,1,2)
fig = plt.gcf()
fig.subplots_adjust(right=0.68)
plt.plot(freq_domain_magnitude_db)
plt.title('Ch1: FFT')
plt.show()