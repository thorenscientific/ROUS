# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2015-2019 Analog Devices, Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Modified versions of the software must be conspicuously marked as such.
# - This software is licensed solely and exclusively for use with
#   processors/products manufactured by or for Analog Devices, Inc.
# - This software may not be combined or merged with other code in any manner
#   that would cause the software to become subject to terms and conditions
#    which differ from those listed here.
# - Neither the name of Analog Devices, Inc. nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# - The use of this software may or may not infringe the patent rights of one
#   or more patent holders. This license does not release you from the
#   requirement that you obtain separate licenses from these patent holders
#   to use this software.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# NON-INFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# DAMAGES ARISING OUT OF CLAIMS OF INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT;
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# 2019-01-10-7CBSD SLA
# -----------------------------------------------------------------------

'''
LinearLabTools simulation of pulse characterization. Many mixed-signal
applications involve characterizing pulses - seismic energy exploration,
analyzing photomultiplier outputs, etc. This script generates a perfect
Gaussian pulse, but adds a random component to the width, position in time,
and amplitude. Two techniques are then used to characterize the pulse;
simple convolution with another pulse


Tested with Python 2.7, Anaconda distribution available from Continuum Analytics,
http://www.continuum.io/
'''

import numpy as np
from matplotlib import pyplot as plt



# unknown pulse parameters
alt = 1.0
mean = 350.0
sigma = 5
noise = 0.2

# ADC Noise parameters

#adc_noise = (10 ** (adc_snr / 20)) * adc_range / (2*2**0.5)
#ADC RMS noise formula: 10^(SNR / 20) * peak-to-peak input range /(2*SQRT2) = RMS Noise


#From the datasheet: 10^(-104dB SNR / 20) * 10V/(2*SQRT2) = 22.3uVRMS
ltc2387_noise = (10 ** (-96.0 / 20)) * 8.192 / (8.0**0.5)
ltc2269_noise = (10 ** (-84.0 / 20)) * 2.1 / (8.0**0.5)
print("LTC2387 RMS noise: " + str(ltc2387_noise))
print("LTC2269 RMS noise: " + str(ltc2269_noise))

def bellcurve(x,alt,mean,sigma):
    return alt*np.exp(-1*((x-mean)**2.0)/(2.0*sigma**2.0))

unknown_pulse = np.ndarray(shape=1000, dtype=float)
testpulse = np.ndarray(shape=100, dtype=float)

for i in range(0, 100): # First, make test pulse
    j = float(i)
    testpulse[i] = bellcurve(j, 1, 50, 10.0)
#testpulse = testpulse * np.hanning(testpulse.size)

for i in range(0, 1000):
    j = float(i)
    unknown_pulse[i] = bellcurve(j, alt, mean, sigma) + np.random.normal(loc=0.0, scale = noise)

position_vector = np.convolve(unknown_pulse, testpulse[::-1])
print("Maximum correlation at " + str(np.argmax(position_vector) - 50))

plt.figure(1)
plt.title("Basic detection\n by convolution")
plt.plot(position_vector)
plt.plot(unknown_pulse)
plt.plot(testpulse)
plt.show()

# Example wavelet transform, based on example given in cwt documentation

from scipy import signal
sig = (np.random.rand(100) - 0.5) * .01
sig += signal.ricker(100, 4)

sig = unknown_pulse

wavelet = signal.ricker
widths = np.arange(1, 20)
cwtmatr = signal.cwt(sig, wavelet, widths)
plt.figure(2)

plt.title("Pulse detection\n by Continuous Wavelet Transform")

#From scipy.signal.cwt example
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.cwt.html

plt.imshow(cwtmatr, extent=[-1, 1, 1, 31], cmap='PRGn', aspect='auto',
           vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
plt.show()

#cwtmatr_xpose = map(list, zip(*cwtmatr))

#plt.plot(cwtmatr_xpose)

plt.figure(3)
points = 100
a = 5.0
vec2 = signal.ricker(points, a)
print(len(vec2))
plt.plot(vec2)
plt.show()
