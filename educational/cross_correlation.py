# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2017-2019 Analog Devices, Inc. All rights reserved.
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
Welcome to the LinearLabTools simulation of a basic cross-correlation noise
measurement. This technique is used in phase noise measurements, where the
instrument noise is greater than the noise of the device under test. The
way around this is to make TWO instrument paths, whose noise will be uncorrelated.
The instrument path outputs will have a correlated component due to the common DUT
noise at the input.

This program shows how to extract the correlated component

Inspired by this article:
http://www.holzworth.com/Aux_docs/Holz_MWJ_TechFeat_Feb2011.pdf

'''

import numpy as np
from numpy import array, vdot, zeros
from scipy import fft, real
#from numpy.random import normal, uniform

# For some reason, numpy dot product functions don't do what we expect. This could
# be a misunderstanding. Not a big deal, let's test out a couple of functions to do this:
def dot_product(a,b):
    dp=np.real(a)*np.real(b) + np.imag(a) * np.imag(b)
    return dp

def alt_dot_product(a, b):
    dp = np.abs(a)*np.abs(b)*np.cos(np.angle(a) - np.angle(b))
    return dp

a = array([1+2j,3+4j])
b = array([5+6j,7+8j])

c = 2+2j
d = 2+2j

#print vdot(a, b)
#(70-8j)
#print vdot(b, a)
#(70+8j)
print (np.dot(c, d))
print (np.vdot(c, d))
print (dot_product(c, d))
print (alt_dot_product(c, d))



zero_vector = np.ndarray(shape=(1024), dtype=complex) # Make a complex vector
xcorr = zero_vector

'''############################'''
'''Set up simulation parameters'''
'''############################'''

num_points = 1024    # Number of time-domain points (which is also the number of freq. domain points)
dut_noise_level = 0.1       # Noise of the device under test
tester_noise = 0.5   # Noise of each of the test instrument's signal paths
naverages = 1000      # Number of captures to average. The more captures you average, the closer the end result will
                     # be to the DUT noise

# Make a small "pilot tone" - this produces a spur in the frequency plot that is easy to identify.
# This is just for testing, as something that is a bit more intuitive to look at than pure noise.
pilot_tone_bin = 100
pilot_tone_amp = .02


dut_noise_fft_avg = zeros(num_points)
path_a_noise_fft_avg = zeros(num_points)
path_b_noise_fft_avg = zeros(num_points)
xcorr_avg = zeros(num_points)

zero_vector = np.ndarray(shape=(num_points), dtype=complex) # Make a complex vector
xcorr = zero_vector


for j in range(0, naverages):
    random_phase = np.random.uniform(0.0, 2*3.1415926, 1) # Random phase for the pilot tone
    dut_noise = np.random.normal(0.0, dut_noise_level, num_points) # Time-domain vector of DUT noise
    for i in range(0, num_points):
        dut_noise[i] += pilot_tone_amp * np.sin(random_phase + (2.0*3.1415926 * pilot_tone_bin * i/num_points))

    path_a_noise = np.random.normal(0.0, tester_noise, num_points) # Noise of one of the tester's signal paths
    path_b_noise = np.random.normal(0.0, tester_noise, num_points) # Noise of the tester's other signal path

    dut_noise_fft = fft(dut_noise) # FFT of DUT noise, for comparison to cross-correlation result
    path_a_noise_fft = fft(path_a_noise + dut_noise) # FFT of the two tester path outputs. DUT noise
    path_b_noise_fft = fft(path_b_noise + dut_noise) # is common between the two.


    for i in range(0, num_points): # Dot product of each individual bin
        xcorr[i] = (dot_product(path_a_noise_fft[i], path_b_noise_fft[i]))

    # Sum all FFTs
    dut_noise_fft_avg = dut_noise_fft_avg + abs(dut_noise_fft)
    path_a_noise_fft_avg = path_a_noise_fft_avg + abs(path_a_noise_fft)
    path_b_noise_fft_avg = path_b_noise_fft_avg + abs(path_b_noise_fft)
    xcorr_avg = xcorr_avg + xcorr

# Divide all FFTs by number of averages
dut_noise_fft_avg = dut_noise_fft_avg / naverages
path_a_noise_fft_avg = path_a_noise_fft_avg / naverages
path_b_noise_fft_avg = path_b_noise_fft_avg / naverages
xcorr_avg = xcorr_avg / naverages

# Take square-root to account for the fact that xcorr_avg was a straight average,
# not RSS
for i in range(0, num_points):
    xcorr_avg[i] = pow(xcorr_avg[i], 0.5)


#print path_a_noise_fft[0]

#xcorr[0] = vdot(path_a_noise_fft[0], path_b_noise_fft[0])

#print real(xcorr)

from matplotlib import pyplot as plt

# Plot!

#plt.plot(t, s, t, i)
plt.figure(1)

plt.subplot(411)
plt.title('Path A noise')
plt.plot(abs(path_a_noise_fft_avg))

plt.subplot(412)
plt.title('Path B noise')
plt.plot(abs(path_b_noise_fft_avg))

plt.subplot(413)
plt.title('DUT noise')
plt.plot(abs(dut_noise_fft_avg))

plt.subplot(414)
plt.title('Cross correlation avg, should approach DUT noise')
plt.plot(abs(xcorr_avg))
plt.show()

#plt.figure(2)
#
#plt.subplot(411)
#plt.plot(abs(path_a_noise_fft))
#plt.title('Last data')
#plt.subplot(412)
#plt.plot(abs(path_b_noise_fft))
#plt.subplot(413)
#plt.plot(abs(dut_noise_fft))
#plt.subplot(414)
#plt.plot(abs(xcorr))
#plt.show()

#print dut_noise
