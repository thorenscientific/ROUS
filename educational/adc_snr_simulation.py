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
Welcome to the LinearLabTools simulation of basic FFT operation, SNR calculation
Basically, we're making a vector of num_bins time domain
samples, then corrupting the signal in several "real world" ways:

1) Thermal noise is added to the signal, which is just a random
number with a gaussian distribution. This is often referred to as the
"transition noise" of an ADC, and it can never be smaller than K*T/C where
K is Boltzmann's constant, T is absolute temperature, and C is the size of the
ADC's sample capacitor.

2) Quantization noise is added by simply starting with a signal of amplitude
2^(number of bits), then truncating the decimal portion with the int function

3) Random jitter is added to the sample clock. This is an accurate model of
wideband clock jitter that is spread across seveal Nyquist bands

3) Deterministic jitter is added to the sample clock, representing phase noise
at a particular frequency. This gives an intuitive understanding of the effect
of phase noise as a signal's frequency and amplitude change.

'''

'''############################'''
'''Set up simulation parameters'''
'''############################'''
bits = 16 # ADC resolution (Theoretical!!)
num_bins = 4096 #This is also the number of points in the time record

#Bin number of the signal itself. If bin_number is greater
#than num_bins/2, then the signal will be aliased accordingly.
# Also, this simulation does not handle non-integer (noncoherent)
# bin numbers. (Application of windows is a big topic in and of itself.)

bin_number = 10.01234 

thermal_noise = 0.5 #0.00010 # LSB of thermal noise
jitter = 0.0000000000001 #0.000025 # clock jitter, expressed as RMS fraction of a sampling interval

# Now for some phase noise... To illustrate the concept, we're going to introduce
# a single tone of phase noise, rather than a distribution (as is the case in
# "real life".) This IS an accurate representation of a sinusoidal disturbance
# on the clock.

phase_noise_offset = 25 # Offset from carrier in bins
phase_noise_amplitude = 0.0 #.000001 #Amplitude, in fraction of a sample period
'''##############################'''
'''END set up simulation parameters'''
'''##############################'''

# Pull in the good stuff from various libraries...
import numpy as np
from scipy import fft
from matplotlib import pyplot as plt

# declare variables to make code easier to read below
data = np.zeros(num_bins)
freq_domain_signal = np.zeros(num_bins)
freq_domain_noise = np.zeros(num_bins)

signal_level = 2.0**bits # Calculated amplitude in LSB.

#Generate some input data, along with noise
for t in range(num_bins):
    phase_jitter = phase_noise_amplitude * np.cos(2.0 * np.pi * phase_noise_offset* t / num_bins)
    samp_jitter = np.random.normal(0.0, jitter)
    data[t] = signal_level * np.cos(2.0*np.pi*bin_number*(t + samp_jitter + phase_jitter)/num_bins)/2.0 #First the pure signal :)
    data[t] += np.random.normal(0.0, thermal_noise) #Then the thermal noise ;(
    data[t] = np.rint(data[t]) #Finally, round to integer value - equiavalent to quantizing

freq_domain = np.fft.fft(data)/num_bins
freq_domain_magnitude = np.abs(freq_domain)

#Now notch the signal out of the spectrum. We have the advantage here
#that there's only a single bin of signal, and no distortion.
np.copyto(freq_domain_noise, freq_domain_magnitude) #Make a copy
freq_domain_noise[int(bin_number)] = 0 #Zero out positive signal bin
freq_domain_noise[num_bins - int(bin_number)] = 0 # And the negative bin
# Note that we're also zeroing out one bin worth of noise. We're going to assume this is insignificant
# in this simulation, but if you're zeroing out lots of bins with a mask, you might want to fill them in
# with the average noise floor from the bins that aren't zeroed (or some more intelligent estimate.)


#Make another array that just has the signal
freq_domain_signal[int(bin_number)] = freq_domain_magnitude[int(bin_number)]
freq_domain_signal[num_bins - int(bin_number)] = freq_domain_magnitude[num_bins - int(bin_number)]

signal = 0.0 #Start with zero signal, zero noise
noise = 0.0

# Sum the power root-sum-square in each bin. Abs() function finds the power, a resistor dissipating
# power does not care what the phase is!

signal_ss = np.sum(((freq_domain_signal)) ** 2)
noise_ss = np.sum(((freq_domain_noise)) ** 2 )

signal = np.sqrt(signal_ss) / num_bins
noise = np.sqrt(noise_ss) / num_bins

snr_fraction = signal / noise
snr = 20*np.log10(signal / noise)
print ("Signal: " + str(signal))
print ("Noise: " + str(noise))
print ("Fractional signal to noise: " + str(snr_fraction))
print ("SNR: " + str(snr) + "dB")

max_freq_domain_magnitude = max(freq_domain_magnitude)
freq_domain_magnitude_db = 20 * np.log10(freq_domain_magnitude / max_freq_domain_magnitude)

plt.figure(1)
plt.title("Time domain data, with imperfections")
plt.plot(data)
plt.show

plt.figure(2)
plt.title("Spectrum")
plt.plot(freq_domain_magnitude_db)
plt.show

