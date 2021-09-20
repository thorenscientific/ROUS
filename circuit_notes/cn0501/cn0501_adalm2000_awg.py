# Copyright (C) 2021 Analog Devices, Inc.
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
# RIGHTS, PROCUREMENT OF SUBSTIT11111111111111111111111111111111111111111111111111111111111111111111UTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
print("Program start")

import math
import pandas as pd
import time
from scipy.signal import periodogram,find_peaks,ricker
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
print("Python Packages Import done")

from adi.ad7768 import ad7768
import libm2k
from sin_params import *
print("ADI Packages Import done")

import cn0501_aux_functions

cwd = os.getcwd()
fpath = cwd + "\\csv_files\\"
print ("Filepath: " + fpath)

def test_param():
    #GEOPHONE A0:A1:A2
    #ADXL A4:A5:A6
    global loops,ch,fname,nsecs

    #print("\nHow many loops?")
    loops = 1
    #print("\nWhat channel?")
    ch = 0

    #print("\n # Seconds record")
    nsecs = 2

    #print("\nExport filename?")
    fname = "ch"+str(ch)

# This should eventually move into adi folder, and add an import to __init__
class cn0501(ad7768):
    def __init__(self, uri=""):
        ad7768.__init__(self, uri=uri)

    def single_capture(self):
        self.power_mode = "FAST_MODE" #FAST_MODE MEDIAN_MODE LOW_POWER_MODE
        self.filter = "WIDEBAND"
        self.sample_rate = 8000
        self.rx_buffer_size = 16384
        x = self.rx()
        print("enabled channels: ")
        print(self.rx_enabled_channels)
        return x
        #max 512000




hardcoded_ip = 'ip:analog.local'
print("args:\n", sys.argv)
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip
m2k_ip = sys.argv[2] if len(sys.argv) >= 3 else None

test_param()
# Instantiate hardware
my_m2k = cn0501_aux_functions.wav_init()
my_cn0501 = cn0501(uri=my_ip)

# Pick One:
#cn0501_aux_functions.wavdiff_out(my_m2k)
cn0501_aux_functions.seismic_out(my_m2k)
#cn0501_aux_functions.sine_1k_out(my_m2k)
#cn0501_aux_functions.wavsingle_out(my_m2k)


#mycn0501.run_sample_rate_tests()
data = my_cn0501.single_capture()
data[0] -= np.average(data[0]) # Remove DC
cn0501_aux_functions.wav_close(my_m2k)
del my_cn0501
del my_m2k

plt.figure(2)
plt.subplot(2,1,1)
plt.tight_layout()
plt.title("Captured data")
plt.xlabel("Data point")
plt.ylabel("Volts")
plt.plot(data[0])
plt.subplot(2,1,2)
plt.tight_layout()
plt.title("FFT")
plt.xlabel("FFT bin")
plt.ylabel("Amplitude, dBFS")
plt.plot(20*np.log10(windowed_fft_mag(data[0])))
plt.ylim(-160, 10)
plt.show()


harmonics, snr, thd, sinad, enob, sfdr, floor = sin_params(data[0])
print("A.C. Performance parameters (ONLY valid for a sine input):")
print("Harmonics:", harmonics)
print("snr: ", thd)
print("Sinad: ", sinad)
print("ENOB: ", enob)
print("SFDR: ", sfdr)
print("Noise Floor: ", floor)

#    return(data[0])
#mydata = main()

'''
'''

