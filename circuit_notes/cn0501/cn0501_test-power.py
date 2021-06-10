# Copyright (C) 2020 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
print("Program start")

from scipy.signal import periodogram,find_peaks,ricker
import matplotlib.pyplot as plt
from adi import ad7768
import numpy as np
import libm2k
import pandas as pd
import math
import time

print("Import done")

ctx=libm2k.m2kOpen()
if ctx is None:
    print("Connection Error: No ADALM2000 device available/connected to your PC.")
    exit(1)

loops = 0
ch = 0
freq = 0
amplitude = 0
fname = ""

def test_param():
    #GEOPHONE A0:A1:A2
    #ADXL A4:A5:A6
    global loops,ch,freq,fname,amplitude
    print("\nHow many loops?")
    #loops = int(input())
    loops = 3
    print("\nWhat channel?")
    #ch = int(input())
    ch = 0
    print("\nSine Frequency/ Num of Ricker peaks?")
    #freq = float(input())
    freq = 1
    print("\nSine/Ricker amplitude?")
    #amplitude1 = float(input())
    amplitude = 5

    print("\nExport filename?")
    #fname = input()
    #fname = "ch"+str(ch)+"_npks"+str(freq)+"_scale_5_1"
    fname = "power_test"

def m2k():
    ctx.calibrateDAC()
    aout=ctx.getAnalogOut()  

    #Sine wave
    #Frequency in Hertz
    f = freq
    #Samples per second
    N = 750000
    #Peak amplitude in Volts
    vpeak = amplitude/2
    #DC offset in volts
    offset = vpeak

    x=np.arange(0,1,1/N)

    sine_func= vpeak*np.sin(2*np.pi*f*x) + offset

    #Ricker wavelet
    vpp = amplitude #pk-pk amplitude of wavelet
    n_peak=int(freq) #Number of wavelet peaks
    n_points = int(N/n_peak) #number of points per wavelet
    width_param = int(n_points*.05) #5% width parameter
    x = ricker(n_points,width_param) #generate wavelet
    v_scale = vpp/(np.max(x)-np.min(x)) #scale to fit vpp
    x= v_scale*x

    rick_offset = 0 - np.min(x)
    x = x+rick_offset #Adjust Wavelet to fit 0 to V(amplitude)

    
    if n_peak > 1:
        ricker_wav = np.concatenate((x,x))
        for _ in range(1,n_peak-1):
            ricker_wav= np.concatenate((ricker_wav,x))
    else:
        ricker_wav = x

    

    ramp_f = np.linspace(0,amplitude, num = N)
    fixed_dc = amplitude*np.ones(N)

    print("Test value") 
    print(len(ramp_f))

    #buffer2 = sine_func
    buffer2 = ricker_wav
    #buffer2 = ramp_f
    #buffer2 = fixed_dc
    buffer1 = buffer2

    aout.setSampleRate(0, N)
    aout.setSampleRate(1, N)
    aout.enableChannel(0, True)
    aout.enableChannel(1, True)

    buffer = [buffer1, buffer2]

    aout.setCyclic(True)
    aout.push(buffer)

    m2k_out = np.asarray(buffer2)
    m2k_out = m2k_out.reshape(N,1)

    DF = pd.DataFrame(m2k_out)
    f = fname + "_stimuli.csv"
    print(f)
    #File directory of exported csv files 
    DF.to_csv(r"C:\Users\VCalinao\pyadi-iio\examples\csv_files\\"+f, index = False, header = False)

def cn0501():
    adc = ad7768(uri="ip:10.116.177.41")
    #adc.sample_rate = 256000
    adc.power_mode = "FAST_MODE" #FAST_MODE MEDIAN_MODE LOW_POWER_MODE
    adc.filter = "SINC5"

    adc.sample_rate = 32000

    print("Buffer size")
    print(adc.rx_buffer_size)

    print("Enabled Channels")
    print (adc.rx_enabled_channels)

    sec_rec = math.ceil(adc.sample_rate/adc.rx_buffer_size)
    '''
    print("\nHow many loops?")
    loops = int(input())
    print("\nWhat channel?")
    ch = int(input())
    print("\nExport filename?")
    fname = input()
    '''
    print("\nSTART RECORD\n")

    for nloop in range(0,loops):
        print(nloop)
        vdata = []
        count = 0
        start = time.time()
        for _ in range(int(sec_rec)):
                data = adc.rx() 
                vdata.append(data[ch])
                count += len(data[ch])
        end = time.time()
        
        c = (end - start)
        print("Elapsed: " + str(c))
        #print(c.total_seconds())

        vdata_arr = np.asarray(vdata)
        vdata_arr = vdata_arr.reshape(count,1)

        DF = pd.DataFrame(vdata_arr)
        f = fname + "_loop" + str(nloop)+".csv"
        print(f)
        #File directory of exported csv files 
        DF.to_csv(r"C:\Users\VCalinao\pyadi-iio\examples\csv_files\\"+f, index = False, header = False)
    print("Export done")
    #print(len(vdata_arr))
    #npeaks = find_peaks(s)
    #print(npeaks)
    
    x = np.arange(0,1,1/len(vdata_arr))
    plt.plot(x,vdata_arr)
    plt.show()


def main():
    test_param()
    m2k()
    cn0501()

    print("Close M2K handler")
    libm2k.contextClose(ctx)

main()

'''
'''

