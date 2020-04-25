'''
AD7768-FMCZ Zedboard data capture, plot, save module

Provides a single functon that returns a list of lists of individual channel data
Optionally analyzes and plots all channels and / or save data to a file

testdata = eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = True,
                             do_write_to_file = True)

ToDo - add options for ADC sample rate and ADC filter type
Note that filter type is not supported in the Linux driver yet.
'''

import llt
from matplotlib import pyplot as plt
import libm2k
import numpy as np
from time import sleep

import llt.demo_board_examples.ad_adc.ad7768.eval_ad7768_fmcz_pyadi_iio as my_ad7768

import sys
NUM_SAMPLES = 8 * 1024
buflen = 8192
hardcoded_ip = 'ip:10.26.148.118' #118
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip


my_m2k=libm2k.m2kOpen()
my_m2k.calibrateADC()
my_m2k.calibrateDAC()

aout=my_m2k.getAnalogOut()

print(aout.setSampleRate(0, 75000))
print(aout.setSampleRate(1, 75000))
aout.enableChannel(0, True)
aout.enableChannel(1, True)

x=np.linspace(-np.pi,np.pi,2048)
buffer1=np.linspace(-2.0,2.00,2048)
buffer2=np.sin(x)
ricker = [0]*2048

print ("reading seismic_pulse_ricker.csv")
with open('seismic_pulse_ricker.txt', 'r') as infile: # Read in coefficients from files
    for i in range(0, 2048):
        instring = infile.readline()
        ricker[i] = float(instring)

buffer = [buffer2, ricker]

aout.setCyclic(True)
aout.push(buffer)
sleep(0.5)


# to use this function in your own code to just grab samples, you would
# typically do:
# eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=False, do_plot = False,
#                        do_write_to_file = False)
#testdata = my_ad7768.eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = False,
#                             do_write_to_file = True)


try:
    import adi
    sleep(0.5)
except:
    print ("pyadi-iio not found!")
    sys.exit(0)

buflen = NUM_SAMPLES

try:
    adi.context_manager.uri="ip:10.26.148.119"
    myadc=adi.ad7768()
    myadc.rx_buffer_size = 8*1024
except:
    print("No device found")
    sys.exit(0)

testdata = myadc.rx()
del myadc







libm2k.deviceClose(my_m2k)
del my_m2k

plt.figure(1)
plt.plot(testdata[0])
plt.show()

plt.figure(2)
plt.plot(testdata[1])
plt.show()

plt.figure(3)
plt.plot(testdata[2])
plt.show()

plt.figure(4)
plt.plot(testdata[3])
plt.show()

plt.figure(5)
plt.plot(testdata[4])
plt.show()

plt.figure(6)
plt.plot(testdata[5])
plt.show()

plt.figure(7)
plt.plot(testdata[6])
plt.show()

plt.figure(8)
plt.plot(testdata[7])
plt.show()



