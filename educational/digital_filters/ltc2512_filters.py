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
LTC2512_filters.py

This script imports the LTC2512 digital filter coefficents and plots the
impulse responses and frequency responses.
It then calculates the "effective noise bandwidth" in two ways, by measuring
the filter's effect on a set of random data, and by direct integration of the
frequency response.

Tested with Python 2.7, Anaconda distribution available from Continuum Analytics,
http://www.continuum.io/
'''

# Import standard libraries
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import time

# Import Linear Lab Tools utility funcitons
import sys
import llt.utils.linear_lab_tools_functions as lltf

start_time = time.time();

# Which method to use to calculate frequency response from filter coefficients. The freqz method is
# the "traditional" way, but the FFT method is considerably faster.
use_fft_method = True
ppc = 8 # Points per coefficient, affects fft method
num_freqencies = 65536 # Number of frequencies to evaluate, affects freqz method

# Initialize arrays to hold filter coefficients. We know the number of elements ahead of time.
ssinc_flat_4 = np.ndarray(117, dtype=float)
ssinc_flat_8 = np.ndarray(235, dtype=float)
ssinc_flat_16 = np.ndarray(471, dtype=float)
ssinc_flat_32 = np.ndarray(943, dtype=float)
#ssinc_flat_64 = np.ndarray(1887, dtype=float)

# Read in coefficients from files
with open('../../../common/ltc25xx_filters/ssinc_flat_4.txt', 'r') as infile:
    for i in range(0, 117):
        instring = infile.readline()
        ssinc_flat_4[i] = float(instring)
print('done reading DF 4!')

with open('../../../common/ltc25xx_filters/ssinc_flat_8.txt', 'r') as infile:
    for i in range(0, 235):
        instring = infile.readline()
        ssinc_flat_8[i] = float(instring)
print('done reading DF 8!')

with open('../../../common/ltc25xx_filters/ssinc_flat_16.txt', 'r') as infile:
    for i in range(0, 471):
        instring = infile.readline()
        ssinc_flat_16[i] = float(instring)
print('done reading DF 16!')

with open('../../../common/ltc25xx_filters/ssinc_flat_32.txt', 'r') as infile:
    for i in range(0, 943):
        instring = infile.readline()
        ssinc_flat_32[i] = float(instring)
print('done reading DF 32!')

#with open('../../common/ltc25xx_filters/ssinc_flat_64.txt', 'r') as infile:
#    for i in range(0, 1887):
#        instring = infile.readline()
#        ssinc_flat_64[i] = float(instring) # Frequency Density
#print('done reading DF 64!')
ssinc_flat_4 /= sum(ssinc_flat_4) #Normalize to unity gain
ssinc_flat_8 /= sum(ssinc_flat_8) #Normalize to unity gain
ssinc_flat_16 /= sum(ssinc_flat_16) #Normalize to unity gain
ssinc_flat_32 /= sum(ssinc_flat_32) #Normalize to unity gain
#ssinc_flat_64 /= sum(ssinc_flat_64) #Normalize to unity gain
print("Done normalizing!")

# Plot the impulse responses on the same horizontal axis, with normalized
# amplitude for a better visual picture...
plt.figure(1)
plt.title('LTC2512 SSinc + Flattening filter impulse responses (DF 8, 16, 32, 64)')
plt.plot(ssinc_flat_4 / max(ssinc_flat_4))
plt.plot(ssinc_flat_8 / max(ssinc_flat_8))
plt.plot(ssinc_flat_16 / max(ssinc_flat_16))
plt.plot(ssinc_flat_32 / max(ssinc_flat_32))
#plt.plot(ssinc_flat_64 / max(ssinc_flat_64))
plt.xlabel('tap number')
plt.show()

# Function to calculate frequency response of a filter from its coefficients.
# The points_per_coeff parameter tells how many points
# in between unit circle zeros to calculate.
#def freqz_by_fft(filter_coeffs, points_per_coeff):
#    num_coeffs = len(filter_coeffs)
#    fftlength = num_coeffs * points_per_coeff
#    resp = abs(np.fft.fft(np.concatenate((filter_coeffs,
#               np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
#    return resp

if(use_fft_method == True):
    print("Calculating frequency response using zero-padded FFT method")
    ssinc_flat_4_mag = lltf.freqz_by_fft(ssinc_flat_4, 128*ppc)
    ssinc_flat_8_mag = lltf.freqz_by_fft(ssinc_flat_8, 64*ppc)
    ssinc_flat_16_mag = lltf.freqz_by_fft(ssinc_flat_16, 16*ppc)
    ssinc_flat_32_mag = lltf.freqz_by_fft(ssinc_flat_32, 4*ppc)
#    ssinc_flat_64_mag = lltf.freqz_by_fft(ssinc_flat_64, ppc)
else:
    print("Calculating frequency response using numpy's freqz function")
    w0, ssinc_flat_4_mag = signal.freqz(ssinc_flat_4, 1, num_freqencies)
    w1, ssinc_flat_8_mag = signal.freqz(ssinc_flat_8, 1, num_freqencies)
    w2, ssinc_flat_16_mag = signal.freqz(ssinc_flat_16, 1, num_freqencies)
    w3, ssinc_flat_32_mag = signal.freqz(ssinc_flat_32, 1, num_freqencies)
#    w4, ssinc_flat_64_mag = signal.freqz(ssinc_flat_64, 1, num_freqencies)

# Calculate response in dB, for later use...
ssinc_flat_4_db = 20*np.log10(abs(ssinc_flat_4_mag))
ssinc_flat_8_db = 20*np.log10(abs(ssinc_flat_8_mag))
ssinc_flat_16_db = 20*np.log10(abs(ssinc_flat_16_mag))
ssinc_flat_32_db = 20*np.log10(abs(ssinc_flat_32_mag))
#ssinc_flat_64_db = 20*np.log10(abs(ssinc_flat_64_mag))

# Plot frequency response, linear frequency axis
plt.figure(2)
plt.semilogy(ssinc_flat_4_mag, zorder=1)
plt.semilogy(ssinc_flat_8_mag, zorder=1)
plt.semilogy(ssinc_flat_16_mag, zorder=1)
plt.semilogy(ssinc_flat_32_mag, zorder=1)
#plt.semilogy(ssinc_flat_64_mag, zorder=1)


plt.title('LTC2512 SSinc filter responses (DF 4, 8, 16, 32)')
plt.xlabel('freq.')
plt.ylabel('log Amplitude')
plt.axis([0, 16400, 10.0**(-150/20), 1])
plt.show()

# Next, let's see what the noise reduction properties of the filters are,
# first using "brute force", that is, create an array of noisy data with a
# known RMS value, then see how much the filter reduces the noise. For example,
# if the noise is reduced by a factor of 2, then the bandwidth has been reduced
# by a factor of 4. You don't necessarily know which FREQUENCIES were cut out,
# but the EFFECTIVE noise bandwidth is what we're after.
# Next, we'll double check by actually integrating the filter's noise response.

filter2check = ssinc_flat_16 # Choose which filter to check...
filtermag2check = ssinc_flat_16_mag # And its magnitude response
numpoints = 2**20 # Start with a million noisy data points, RMS = 1.0
noisydata = np.random.normal(loc=0, scale=1.0, size=numpoints)
rms_noise = np.std(noisydata) # Actual noise will vary a bit... double-check
print("RMS noise of original data: " + str(rms_noise))
filtered_data_16 = np.convolve(filter2check, noisydata, 'valid') # Filter the data
filtered_noise = np.std(filtered_data_16) # Find RMS noise of filtered data
print("RMS noise of filtered data: " + str(filtered_noise))
print("noise was reduced by a factor of " + str(filtered_noise/rms_noise))
print("Effective bandwidth of filter: " + str((filtered_noise/rms_noise)**2.0))
# Now let's integrate the filter's magnitude response. Dig into the function
# definition for details, but it basically squares the response, integrates,
# then takes the square-root at each point. The second argument is the
# bandwidth that each point represents, so we'll normalize to unity.

integral = lltf.integrate_psd(filtermag2check, 1.0/len(filtermag2check))
plt.figure(3)
plt.title("Integrated Noise")
plt.plot(integral)
plt.show()
# The last element is the total noise that "gets through" the filter
enbw = integral[len(integral)-1] ** 2.0
print("Effective bandwidth by integrating PSD: " + str(enbw))

print "My program took", (time.time() - start_time), " seconds to run"