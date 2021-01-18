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
Simple demonstration of extracting the phase difference between two signals.
So far it's pretty friendly, only sinusoids with random noise, same noise level
for both signals.

An integer bin number implies coherent sampling, use a fractional bin to try
to confuse the phase detection.

'''

# Pull in the good stuff from various libraries...
import numpy as np
from matplotlib import pyplot as plt

'''############################'''
'''Set up simulation parameters'''
'''############################'''
bits = 16 # ADC resolution (Theoretical!!)
num_bins = 4096 #This is also the number of points in the time record
bin_number = 50.5001 #Bin number of the signal itself. If bin_number is greater
                #than num_bins/2, then the signal will be aliased accordingly.
                # Also, this simulation does not handle non-integer (noncoherent)
                # bin numbers. (Application of windows is a big topic in and of itself.)

thermal_noise = 0.5 #0.00010 # LSB of thermal noise
jitter = 0.0000000000001 #0.000025 # clock jitter, expressed as RMS fraction of a sampling interval

# Now for some phase noise... To illustrate the concept, we're going to introduce
# a single tone of phase noise, rather than a distribution (as is the case in
# "real life".) This IS an accurate representation of a sinusoidal disturbance
# on the clock.
phase_noise_offset = 25 # Offset from carrier in bins
phase_noise_amplitude = 0.0 #.000001 #Amplitude, in fraction of a sample period

# And finally, the phase difference between the two signals. Ideally, the detected
# phase difference will be exactly equal to this. Set up as random for now,
# could be set to a constant while other imperfections are wiggled around.

actual_phase_diff = np.random.rand() * 2. * np.pi # A random phase difference

'''##############################'''
'''END set up simulation parameters'''
'''##############################'''

# declare variables to make code easier to read below
sig1 = np.zeros(num_bins)
sig2 = np.zeros(num_bins)

signal_level = 2.0**bits # Calculated amplitude in LSB.


#Generate some input sig1, along with noise
for t in range(num_bins):
    sig1[t] = signal_level * np.cos(2.0*np.pi*bin_number*(t)/num_bins)/2.0 #First the pure signal :)
    sig1[t] += np.random.normal(0.0, thermal_noise) #Then the thermal noise ;(
    sig1[t] = np.rint(sig1[t]) #Finally, round to integer value - equiavalent to quantizing
    # Second signal with random phase
    sig2[t] = signal_level * np.cos((2.0*np.pi*bin_number*(t)/num_bins)+actual_phase_diff)/2.0
    sig2[t] += np.random.normal(0.0, thermal_noise) #Then the thermal noise ;(
    sig2[t] = np.rint(sig2[t]) #Finally, round to integer value - equiavalent to quantizing

#window = np.blackman(num_bins)
window = np.ones(num_bins)
window = window / np.sum(window) # Normalize

freq_domain_sig1 = np.fft.fft(sig1 * window)/num_bins
freq_domain_magnitude_sig1 = np.abs(freq_domain_sig1)
freq_domain_phase_sig1 = np.angle(freq_domain_sig1)

freq_domain_sig2 = np.fft.fft(sig2 * window)/num_bins
freq_domain_magnitude_sig2 = np.abs(freq_domain_sig2)
freq_domain_phase_sig2 = np.angle(freq_domain_sig2)

fund_bin = np.argmax(freq_domain_sig1[0:int((num_bins/2)-1)]) # Detect fundamental

phase_sig_1 = freq_domain_phase_sig1[fund_bin]
phase_sig_2 = freq_domain_phase_sig2[fund_bin]
phase_difference = phase_sig_2 - phase_sig_1
error = (actual_phase_diff - phase_difference)
if error > 1.0:
    error -= 2.0*np.pi

print ("Fundamental Bin: ", fund_bin)
print ("Actual phase difference: " + str(actual_phase_diff))
print ("Reference signal phase: " + str(phase_sig_1))
print ("Measurement signal phase: " + str(phase_sig_2))
print ("Measured phase difference: " + str(phase_difference))
print ("Error: ", error)


plt.figure(1)
plt.title("Time domain data, with imperfections")
plt.plot(sig1)
plt.plot(sig2)
plt.show


plt.figure(3)
plt.title("Spectrum")
plt.plot(20*np.log10(freq_domain_magnitude_sig1))
plt.plot(20*np.log10(freq_domain_magnitude_sig2))
plt.show

