'''
AD400xFMCZ super simple data capture example
Tested on Zedboard.

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
import llt.common.functions as funcs

bufflen = 2**13

# Setup Context
hc_ip = 'ip:10.54.6.10' # default hardcoded ip
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hc_ip

try:
    ctx = iio.Context(my_ip)
except:
    print("No device found")
    sys.exit(0)    

rxadc = ctx.find_device("ad4020") # RX/ADC Core in HDL for DMA

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
data = np.frombuffer(x, np.int32)
for i in range(0, len(data)):
  if(data[i] > 2**19):
    data[i] -= 2**20

do_plot = True
do_write_to_file = False
if do_plot:
    funcs.plot(20, data, verbose=True)
if do_write_to_file:
    funcs.write_to_file_32_bit("data.txt", data, verbose=True)
