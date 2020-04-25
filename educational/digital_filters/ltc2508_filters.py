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
LTC2508_filters.py

This script imports the LTC2508 digital filter coefficents and plots the
impulse responses and frequency responses.

It also shows how to combine the responses of an analog anti-aliasing filter and the digital filter
in order to validate that the overall rejection is adequate at the first image frequency (fs) 

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
ssinc_256 = np.ndarray(2175, dtype=float)
ssinc_1024 = np.ndarray(8703, dtype=float)
ssinc_4096 = np.ndarray(34815, dtype=float)
ssinc_16384 = np.ndarray(139263, dtype=float)

# Read in coefficients from files
with open('../../../common/ltc25xx_filters/ssinc_256.txt', 'r') as infile:
    for i in range(0, 2175):
        instring = infile.readline()
        ssinc_256[i] = float(instring)
print('done reading DF 256!')

with open('../../../common/ltc25xx_filters/ssinc_1024.txt', 'r') as infile:
    for i in range(0, 8703):
        instring = infile.readline()
        ssinc_1024[i] = float(instring)
print('done reading DF 1024!')

with open('../../../common/ltc25xx_filters/ssinc_4096.txt', 'r') as infile:
    for i in range(0, 34815):
        instring = infile.readline()
        ssinc_4096[i] = float(instring)
print('done reading DF 4096!')

with open('../../../common/ltc25xx_filters/ssinc_16384.txt', 'r') as infile:
    for i in range(0, 139263):
        instring = infile.readline()
        ssinc_16384[i] = float(instring) # Frequency Density
print('done reading DF 16384!')

ssinc_256 /= sum(ssinc_256) #Normalize to unity gain
ssinc_1024 /= sum(ssinc_1024) #Normalize to unity gain
ssinc_4096 /= sum(ssinc_4096) #Normalize to unity gain
ssinc_16384 /= sum(ssinc_16384) #Normalize to unity gain
print("Done normalizing!")

# Plot the impulse responses
plt.figure(1)
plt.title('LTC2508 SSinc filter impulse responses (DF 256, 1024, 4096, 16384)')
#plt.subplot(4, 1, 1)
#plt.title("DF256")
plt.plot(ssinc_256 / max(ssinc_256))
#plt.axis([0, len(ssinc_16384), 0, max(ssinc_256)])
#plt.subplot(4, 1, 2)
#plt.title("DF1024")
plt.plot(ssinc_1024 / max(ssinc_1024))
#plt.axis([0, len(ssinc_16384), 0, max(ssinc_1024)])
#plt.subplot(4, 1, 3)
#plt.title("DF4096")
plt.plot(ssinc_4096 / max(ssinc_4096))
#plt.axis([0, len(ssinc_16384), 0, max(ssinc_4096)])
#plt.subplot(4, 1, 4)
#plt.title("DF16384")
plt.plot(ssinc_16384 / max(ssinc_16384))
#plt.axis([0, len(ssinc_16384), 0, max(ssinc_16384)])
plt.xlabel('tap number')
plt.show()

# Function to calculate frequency response of a filter from its coefficients. The points_per_coeff parameter tells how many points
# in between unit circle zeros to calculate.
#def freqz_by_fft(filter_coeffs, points_per_coeff):
#    num_coeffs = len(filter_coeffs)
#    fftlength = num_coeffs * points_per_coeff
#    resp = abs(np.fft.fft(np.concatenate((filter_coeffs, np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
#    return resp

if(use_fft_method == True):
    print("Calculating frequency response using zero-padded FFT method")
    ssinc_256_mag = lltf.freqz_by_fft(ssinc_256, 64*ppc)
    ssinc_1024_mag = lltf.freqz_by_fft(ssinc_1024, 16*ppc)
    ssinc_4096_mag = lltf.freqz_by_fft(ssinc_4096, 4*ppc)
    ssinc_16384_mag = lltf.freqz_by_fft(ssinc_16384, ppc)
else:
    print("Calculating frequency response using numpy's freqz function")
    w1, ssinc_256_mag = signal.freqz(ssinc_256, 1, num_freqencies)
    w2, ssinc_1024_mag = signal.freqz(ssinc_1024, 1, num_freqencies)
    w3, ssinc_4096_mag = signal.freqz(ssinc_4096, 1, num_freqencies)
    w4, ssinc_16384_mag = signal.freqz(ssinc_16384, 1, num_freqencies)

# Calculate response in dB, for later use...
fresp1 = 20*np.log10(abs(ssinc_256_mag))
fresp2 = 20*np.log10(abs(ssinc_1024_mag))
fresp3 = 20*np.log10(abs(ssinc_4096_mag))
fresp4 = 20*np.log10(abs(ssinc_16384_mag))

# Plot frequency response, linear frequency axis
plt.figure(2)
plt.semilogy(ssinc_256_mag, zorder=1)
plt.semilogy(ssinc_1024_mag, zorder=1)
plt.semilogy(ssinc_4096_mag, zorder=1)
plt.semilogy(ssinc_16384_mag, zorder=1)


plt.title('LTC2508 SSinc filter responses (DF 256, 1024, 4096, 16384)')
plt.xlabel('freq.')
plt.ylabel('log Amplitude')
plt.axis([0, 16400, 10.0**(-150/20), 1])
plt.show()

# Now let's show the first 2 images of the DF 256 filter, then create an
# analog filter with the intent of suppressing the first image by at least 80dB

sample_rate = 1000000.0
bin_width = sample_rate / len(ssinc_256_mag)
print ("bin width: " + str(bin_width))
print ("1kHz bin: " + str(1000.0 / bin_width))
print ("1kHz bin: " + str(5000.0 / bin_width))

wide_ssinc_256_mag = np.concatenate((ssinc_256_mag, ssinc_256_mag))
first_order_response = np.ndarray(len(wide_ssinc_256_mag), dtype=float)
second_order_response = np.ndarray(len(wide_ssinc_256_mag), dtype=float)
cutoff_1st = 1000.0 / bin_width# 1000.0 # Bin number
cutoff_2nd = 5000.0 / bin_width# 2000.0
for i in range(0, len(wide_ssinc_256_mag)): # Generate first order response for each frequency in wide response
    first_order_response[i] = 1.0 / (1.0 + (i * bin_width /cutoff_1st)**2.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^2)
    second_order_response[i] = 1.0 / (1.0 + (i * bin_width /cutoff_2nd)**4.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^4)



# Create horizontal axis. The "wide" filter response represents DC to 2 x the sample rate.
lw = 3
x = np.linspace(0, (sample_rate * 2) - 1, num=len(wide_ssinc_256_mag))
plt.figure(3)
plt.title("AAF Filter design, SSINC 256, 5kHz 2-pole analog LPF")
plt.axis([200, 0.75*len(wide_ssinc_256_mag), -150, 0])
plt.ylabel("Rejection (dB)")
plt.xlabel("Frequency (Hz)")
#plt.loglog(wide_ssinc_256_mag)
#plt.loglog(first_order_response)
#plt.loglog(second_order_response)

wide_ssinc_256_mag_db = 20*np.log10(wide_ssinc_256_mag)
first_order_response_db = 20*np.log10(first_order_response)
second_order_response_db = 20*np.log10(second_order_response)

plt.semilogx(x, wide_ssinc_256_mag_db, linewidth=lw, color="blue")
#plt.semilogx(x, first_order_response_db, linewidth=lw, color="green")
plt.semilogx(x, second_order_response_db, linewidth=lw, color="red")
#plt.loglog(np.multiply(wide_ssinc_256_mag, second_order_response))
#plt.tight_layout()

# Write out to a file, for video shoot

with open("aaf_design_example.csv", "w") as outfile:
    for i in range(0, len(wide_ssinc_256_mag), 64):
        outfile.write(str(x[i]) + "," +str(wide_ssinc_256_mag_db[i]) + "," +str(second_order_response_db[i]) + "\n")





# Let's get a feel for what exactly each output data point represents. Each data point
# is a weighted sum of samples from the SAR ADC, with weightings according to the
# filter coefficients that we loaded in. But there is overlap from one sample to the
# next, which is what this figure shows.

sscinc_shifted = ssinc_256

plt.figure(4)
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
sscinc_shifted = np.concatenate((np.zeros(256), sscinc_shifted ))
plt.plot(sscinc_shifted)
plt.show()

# So far, we've been plotting "unfolded" frequency responses. That is, what the response
# would be if the digital filter were NOT downsampled by some factor. Let's see what
# the DF256 filter response really is, referred to the ADC's filtered output, which 
# has a data rate of MCLK / DF:

#First, let's get the filter into a really long vector such that when we fold it,
# there are still lots of points to plot per Nyquist zone:
sscinc_256_padded = np.concatenate((ssinc_256, np.zeros(65536 - len(ssinc_256)) ))
ssinc_256_mag_long = lltf.freqz_by_fft(sscinc_256_padded, 1)
ssinc_256_mag_long_dB = 20*np.log10(abs(ssinc_256_mag_long))
#plt.figure(5)
#plt.plot(ssinc_256_mag_long_dB)
#plt.show()

folded_response_zones, folded_response_sum = lltf.fold_spectrum(ssinc_256_mag_long_dB[0:len(ssinc_256_mag_long_dB)/2],
                                                                                 len(ssinc_256_mag_long_dB)/512, 128)
plt.figure(6)

plt.title("SSinc 256 filter response, first 4 nyquist zones")
ax = plt.gca()
ax.set_axis_bgcolor('#D0D0D0')
lines = plt.plot(folded_response_zones[0])
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(folded_response_zones[1])
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(folded_response_zones[2])
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(folded_response_zones[3])
plt.setp(lines, color='#00FF00', ls='--') #Green
#lines = plt.plot(folded_response_sum)
#plt.setp(lines, color='k', ls='-') #Black
plt.show()

# Next, let's see what the noise reduction properties of the filters are,
# first using "brute force", that is, create an array of noisy data with a
# known RMS value, then see how much the filter reduces the noise. For example,
# if the noise is reduced by a factor of 2, then the bandwidth has been reduced
# by a factor of 4. You don't necessarily know which FREQUENCIES were cut out,
# but the EFFECTIVE noise bandwidth is what we're after.
# Next, we'll double check by actually integrating the filter's noise response.

# This takes a long time to run, so make it easy to switch this off
run_noise_reduction_test = False

if run_noise_reduction_test == True:
    filter2check = ssinc_16384 # Choose which filter to check...
    filtermag2check = ssinc_16384_mag # And its magnitude response
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
    plt.figure(7)
    plt.title("Integrated Noise")
    plt.plot(integral)
    plt.show()
    # The last element is the total noise that "gets through" the filter
    enbw = integral[(len(integral))-1] ** 2.0
    print("Effective bandwidth by integrating PSD: " + str(enbw))


print "My program took", (time.time() - start_time), " seconds to run"