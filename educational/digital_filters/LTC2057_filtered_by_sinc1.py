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

"""
    Description:
    This program runs through the basics of a SINC1 (averaging) filter, and how
    to compute the rejection at an arbitrary number of frequencies. It uses
    two functions - the "traditional" freqz function that exists both in Matlab
    and Numpy. The Matlab documentation on Freqz states that if the points requested
    are equally spaced, it uses a zero-padded FFT to calculate the response,
    so we do the same thing as well.
    
    This program also demonstrates how to read in Power Spectral Density data
    from an LTSpice simulation and measure the effect that the digital filter
    has on the total integrated noise.
    
    Open "\common\LTSpice\LTC2057_noisesim_2Meg.asc", run simulation and probe
    node Vout2. Select output graph, then click "File -> Export" and save to
    same directory. This will generate the noise data file required for this
    script to execute.

    Created by: Mark Thoren
    E-mail: mthoren@linear.com
"""

# First, import goodies from standard libraries
import sys
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
# Import Linear Tech functions
# import LTPyLab_functions as lltf
import linear_lab_tools_functions as lltf

# Set up parameters
samplerate = 1024000 # Samples per second

# Make this a multiple of 2. That is, analyze at
# least out to samplerate, which will alias to DC.
nyquist_zones_to_consider = 4

# Select downsample factor. This can be any power of 2 from 4 to 16384
n_factor = 16

# This parameter takes some explanation. When calculating the frequency response of
# the filter, we need more than just n_factor points, because all of the n_factor
# points reside in zeros and you wouldn't have an accurate picture of the response.
freq_response_factor = 512

# Calculate FFT length to use. This is the number of points to analyze for each
# double-nyquist zone.
fftlength = n_factor * freq_response_factor

bin_width = samplerate / (2 * fftlength)

# Next, we'll Generate SINC1 filter coefficients, wich is just a bunch of ones.
# Note that the LTC2380-24 will scale the output automatically for exact
# power-of-2 n_factors, refer to datasheet for scaling of other factors.
sinc1 = np.ones(n_factor)
# Normalize the filter coefficients to unity.
sinc1 = sinc1 / sum(sinc1)

# Compute the frequency response using freqz (traditional method) We're computing
# half the fftlength because freqz gives results halfway around the unit circle,
# while the FFT method below goes all the way around.
w1, sinc1resp_freqz = signal.freqz(sinc1, 1, fftlength/2)
sinc1resp_freqz_dB = 20*np.log10(abs(sinc1resp_freqz))

# You can achieve the same result as the freqz function in a more intuitive way
# by taking an fft of the filter taps, padded out to the length
# of the fft that you will be multiplying the response by.
sinc1resp = abs(np.fft.fft(np.concatenate((sinc1, np.zeros(fftlength - int(sinc1.size)))))) # filter and a bunch more zeros
sinc1resp_dB = 20*np.log10(sinc1resp)
# now plot...
plt.figure(1)
plt.title('sinc1 frequency response from freqz (blue) and\n zero-padded FFT (red), N=' + str(n_factor))
plt.xlabel('frequency bin')
plt.ylabel('Rejection (dB)')
plt.axis([0, fftlength, -50, 0])
lines = plt.plot(sinc1resp_freqz_dB, zorder=1)
plt.setp(lines, color='#0000FF', ls='-') #Blue
lines = plt.plot(sinc1resp_dB)
plt.setp(lines, color='#FF0000', ls='--') #Blue
plt.show()

# Example SPICE directive: .noise V(Vout2) Vin_source lin 16383 62.5 2048000
# Arguments are output node, input node, linear spacing, # of points, bin 1 frequency, end frequency


wide_ltc2057_psd = np.zeros(fftlength*2) # bin zero(DC) already set to zero ;)
print('reading wide (2MHz) noise PSD data from file')
infile = open('LTC2057_noisesim_2Meg.txt', 'r')
print("First line (header): " + infile.readline())
for i in range(1, fftlength*2):
    instring = infile.readline()
    indata = instring.split()         # Each line has two entries separated by a space
    wide_ltc2057_psd[i] = float(indata[1]) # Frequency Density
infile.close()
print('done reading!')

#Okay now let's fold zones.
num_zones = 4
points_per_zone = 4096

zones_ltc2057_psd, ltc2057_folded = lltf.fold_spectrum(wide_ltc2057_psd, points_per_zone, num_zones )

print("Size of zones_ltc2057_psd 2d array:")
print (len(zones_ltc2057_psd))

plt.figure(4)
plt.title("2.048MHz worth of LTC2057 noise,\nFolded into 4 Nyquist zones")
ax = plt.gca()
# ax.set_axis_bgcolor('#C0C0C0')
lines = plt.plot(zones_ltc2057_psd[0])
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(zones_ltc2057_psd[1])
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(zones_ltc2057_psd[2])
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(zones_ltc2057_psd[3])
plt.setp(lines, color='#00FF00', ls='--') #Green
lines = plt.plot(ltc2057_folded)
plt.setp(lines, color='k', ls='-') #Black
plt.show()


# Now multiply zones by filter response!!
total_resp0 = list(zones_ltc2057_psd[0])
total_resp1 = list(zones_ltc2057_psd[1])
total_resp2 = list(zones_ltc2057_psd[2])
total_resp3 = list(zones_ltc2057_psd[3])

# Multipy analog filter response with the digital filter response, zone by zone
for i in range(0, (fftlength//2)-1):
    total_resp0[i] = total_resp0[i] * sinc1resp[i]
    total_resp1[i] = total_resp1[i] * sinc1resp[i]
    total_resp2[i] = total_resp2[i] * sinc1resp[i]
    total_resp3[i] = total_resp3[i] * sinc1resp[i]

# Plot LTC1563 folded response
plt.figure(5)
plt.title("LTC2057 noise to 2.048MHz, folded \nand multiplied by SINC1")
ax = plt.gca()
# ax.set_axis_bgcolor('#C0C0C0')
lines = plt.plot(zones_ltc2057_psd[0])
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(zones_ltc2057_psd[1])
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(zones_ltc2057_psd[2])
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(zones_ltc2057_psd[3])
plt.setp(lines, color='#00FF00', ls='--') #Green
lines = plt.plot(ltc2057_folded)
plt.setp(lines, color='k', ls='-') #Black
 # Plot total response of LTC1563 and digital filter on the same graph.
lines = plt.plot(total_resp0)
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(total_resp1)
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(total_resp2)
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(total_resp3)
plt.setp(lines, color='#00FF00', ls='--') #Green
plt.show()

#



ltc2057_total_noise = np.zeros(fftlength*2)
ltc2057_filtered_total_noise = np.zeros(fftlength//2)
for i in range(1, fftlength*2):
    ltc2057_total_noise[i] = ltc2057_total_noise[i-1] + wide_ltc2057_psd[i]
for i in range(1, fftlength//2-1):
    ltc2057_filtered_total_noise[i] = ltc2057_filtered_total_noise[i-1] + total_resp0[i] + total_resp1[i] + total_resp2[i] + total_resp3[i]
    
ltc2057_total_noise = ltc2057_total_noise / ((bin_width / 2) ** 0.5)
ltc2057_filtered_total_noise = ltc2057_filtered_total_noise  / ((bin_width / 2) ** 0.5)

plt.figure(6)
plt.title("Integrated LTC2057 noise and integrated\nnoise after filtering")
plt.plot(ltc2057_total_noise)
plt.plot(ltc2057_filtered_total_noise)
plt.show()




wide_filter = np.concatenate((sinc1resp, sinc1resp))
wide_filtered_psd = wide_filter * wide_ltc2057_psd


integrated_psd = lltf.integrate_psd(wide_filtered_psd, 1.0)


plt.figure(7)
fig, ax1 = plt.subplots()
plt.title("LTC2057 noise vs. N=16 averaging filter")
ax1.plot(wide_ltc2057_psd, color='#FF0000')
ax1.plot(wide_filter * 0.5* np.max(wide_ltc2057_psd), color='#00FF00')
#ax1.plot(wide_filtered_psd)
ax1.set_ylabel('noise density (V/rootHz)')

ax2 = ax1.twinx()

ax2.plot(integrated_psd * 1000000.0)
ax2.set_ylabel('integrated noise (uV)')
#plt.xlim([0, 4096])
plt.show()

#plt.plot(wide_ltc2057_psd)
#plt.plot(wide_filter * np.max(wide_ltc2057_psd))
#plt.plot(wide_filtered_psd)
#plt.plot(integrated_psd)




'''
fig, ax1 = plt.subplots()
t = np.arange(0.01, 10.0, 0.01)
s1 = np.exp(t)
ax1.plot(t, s1, 'b-')
ax1.set_xlabel('time (s)')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('exp', color='b')
for tl in ax1.get_yticklabels():
    tl.set_color('b')


ax2 = ax1.twinx()
s2 = np.sin(2*np.pi*t)
ax2.plot(t, s2, 'r.')
ax2.set_ylabel('sin', color='r')
for tl in ax2.get_yticklabels():
    tl.set_color('r')
plt.show()
'''









if(False):
    # Now for some more fun... Let's see what the total response of the digital filter and analog
    # AAF filter is. For each point on the frequency axis, a first-order analog AAF with a cutoff
    # frequency of f is multiplied by the digital filter response, then integrated across the whole axis.
    n_factor = 64
    points_per_coeff = 128
    filter_coeffs = np.ones(n_factor) / n_factor # Generate the filter
    fresp = lltf.freqz_by_fft(filter_coeffs, points_per_coeff)
    wide_filter = np.concatenate((fresp, fresp))
    
    
    factor = 16
    first_order_response = np.ndarray(len(wide_filter), dtype=float)
    product_integral = np.ndarray(len(wide_filter)/factor, dtype=float)
    downsampled_wide_filter = np.ndarray(len(wide_filter)/factor, dtype=float)
    
    
    for points in range(1, len(wide_filter)/factor):
        for i in range(0, len(wide_filter)): # Generate first order response for each frequency in wide response
            cutoff = float(points*factor)
            first_order_response[i] = 1.0 / (1.0 + (i/cutoff)**2.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^2)
        print ("Haven't crashed, we're on point " + str(points))
    #    plt.figure(8)
    #    plt.plot(first_order_response)
        composite_response = first_order_response * wide_filter
        datapoint = lltf.integrate_psd(composite_response, 1.0 / (n_factor))
        product_integral[points] = datapoint[len(wide_filter)-1]
        downsampled_wide_filter[points] = wide_filter[points * factor]
    
    product_integral_dB = 20*np.log10(product_integral)
    
    plt.figure(9)
    #plt.plot(wide_filter)
    plt.axis([1, 1024, 0.01, 1])
    plt.loglog(product_integral)
    plt.loglog(downsampled_wide_filter)
    plt.show()
