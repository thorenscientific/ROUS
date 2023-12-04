# Copyright (C) 2022 Analog Devices, Inc.
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


import sys

import adi
import libm2k
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from sine_gen import *
from time import sleep


device_name = "ad4020"
vref = 5.0  # Manually entered, consult eval board manual

# Optionally passs URI as command line argument,
# else use default context manager search
my_uri = sys.argv[1] if len(sys.argv) >= 2 else "ip:analog.local"
print("uri: " + str(my_uri))

my_adc = adi.ad4020(uri="ip:analog.local")
my_adc.rx_buffer_size = 16384

# Set up m2k

ctx=libm2k.m2kOpen()
ctx.calibrateADC()
ctx.calibrateDAC()

siggen=ctx.getAnalogOut()


fs = []
amps = []

for f in range(3000, 300000, 1000): # Sweep 3kHz to 300kHz in 1kHz steps

    #call buffer generator, returns sample rate and buffer
    samp0,buffer0 = sine_buffer_generator(0,f,2,0,180)
    samp1,buffer1 = sine_buffer_generator(1,f,2,0,0)
    
    siggen.enableChannel(0, True)
    siggen.enableChannel(1, True)
    
    siggen.setSampleRate(0, samp0)
    siggen.setSampleRate(1, samp1)
    
    siggen.push([buffer0,buffer1])
    
    sleep(0.25)
    
    #print("Sample Rate: ", my_adc.sampling_frequency)
    print("Frequency: ", f)
    
    data = my_adc.rx()
    data = my_adc.rx()
        
    x = np.arange(0, len(data))
    voltage = data * 2.0 * vref / (2 ** 20)
    dc = np.average(voltage)  # Extract DC component
    ac = voltage - dc  # Extract AC component
    rms = np.std(ac)
    
    fs.append(f)
    amps.append(rms)

amps_db = 20*np.log10(amps/np.sqrt(4.0)) # 4V is p-p amplitude

plt.figure(1)
plt.clf()
plt.title("AD4020 Time Domain Data")
plt.plot(x, voltage)
plt.xlabel("Data Point")
plt.ylabel("Voltage (V)")
plt.show()

f, Pxx_spec = signal.periodogram(
    ac, my_adc.sampling_frequency, window="flattop", scaling="spectrum"
)
Pxx_abs = np.sqrt(Pxx_spec)

plt.figure(2)
plt.clf()
plt.title("AD4020 Spectrum (Volts absolute)")
plt.semilogy(f, Pxx_abs)
plt.ylim([1e-6, 4])
plt.xlabel("frequency [Hz]")
plt.ylabel("Voltage (V)")
plt.draw()
plt.pause(0.05)

plt.figure(3)
plt.title("input filter freq. response")
plt.semilogx(fs, amps_db, linestyle="", marker="o", ms=2)
#plt.ylim([1e-6, 4])
plt.xlabel("frequency [Hz]")
plt.ylabel("response (dB)")
plt.draw()



siggen.stop()
libm2k.contextClose(ctx)

del my_adc
