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
Welcome to the LTPyLab simulation of extraction of
distortion components from a sinusoidal signal. The objective
is to take a sinewave that has a low level of distiortion, and
extract the time-domain components.
'''

'''############################'''
'''Set up simulation parameters'''
'''############################'''
bits = 16 # ADC resolution (Theoretical!!)
num_bins = 4096 #This is also the number of points in the time record
bin_number = 8 #Bin number of the signal itself. If bin_number is greater
                #than num_bins/2, then the signal will be aliased accordingly


num_harmonics = 4 # Let's go up to the fifth harmonic to start...
harmonic_amplitudes = [0.05, 0.1, 0.05, 0.1]
#harmonic_amplitudes = [0.0, 0.0, 0.0, 0.0]

harmonic_phases = [0.0, 0.0, 0.0, 0.0 ]
'''##############################'''
'''END setupsimulation parameters'''
'''##############################'''

# Pull in the good stuff from various libraries...
import numpy as np
from matplotlib import pyplot as plt

# declare variables to make code easier to read below
pure = np.ndarray(shape=num_bins, dtype=float) # The pure sinewave reference signal
distortion = np.ndarray(shape=num_bins, dtype=float) # Just the distortion (added to pure)
data = np.ndarray(shape=num_bins, dtype=float) # The pure sinewave plus distortion components
data_shifted = np.ndarray(shape=num_bins, dtype=float) # A time-shifted version of the data that we will try to correct
data_corrected = np.ndarray(shape=num_bins, dtype=complex) # Corrected (Hopefully!) data, should line up with "data"
freq_domain = np.ndarray(shape=num_bins, dtype=complex)
extracted_dist = np.ndarray(shape=num_bins, dtype=complex)
freq_domain_notched = np.ndarray(shape=num_bins, dtype=complex)
freq_domain_corrected = np.ndarray(shape=num_bins, dtype=complex)
rotation = np.ndarray(shape=num_bins, dtype=complex)

signal_level = 2.0**(bits - 1) # Calculated amplitude in LSB (half of peak-to-peak).


phase = np.random.uniform(-1*np.pi, np.pi, 1) # A random phase shift (radians)
print("Phase: " + str(phase))
timeshift = phase / bin_number # Sample periods
print("Time shift: " + str(timeshift) + " sample periods")

# Make both ideal and shifted waveforms
for t in range(num_bins):

    pure[t]   =       signal_level * np.cos(        2.0*np.pi*bin_number*(t)/num_bins) #First the signal :)
    data[t] = pure[t]
    data_shifted[t] = signal_level * np.cos(phase + 2.0*np.pi*bin_number*(t)/num_bins) #First the signal :)
    for i in range(0, num_harmonics):
        distortion[t] = signal_level * harmonic_amplitudes[i] * np.cos(harmonic_phases[i]+ (2.0*np.pi*bin_number*(i+2)*t)/num_bins)
        data[t] = data[t] + distortion[t]

        distortion[t] = signal_level * harmonic_amplitudes[i] * np.cos(phase*(i+2) + harmonic_phases[i] + (2.0*np.pi*bin_number*(i+2)*t)/num_bins)
        data_shifted[t] = data_shifted[t] + distortion[t]

freq_domain = np.fft.fft(data)/num_bins
freq_domain_phase = np.angle(freq_domain)

freq_domain_shifted = np.fft.fft(data_shifted)/num_bins
freq_domain_shifted_phase = np.angle(freq_domain_shifted)


for f in range(int(num_bins/2)): # Create rotation vector
    rotation[f] = -1.0j * (complex(f*timeshift, 0))
    rotation[num_bins - 1 - f] = 1.0j * (complex((f+1)*timeshift, 0))

rotation_vector = np.exp(rotation)
rotation_angles = np.angle(rotation_vector)

freq_domain_corrected = freq_domain_shifted * rotation_vector # Rotate phases
freq_domain_corrected_phase = np.angle(freq_domain_corrected)
data_corrected = np.fft.ifft(freq_domain_corrected) * num_bins


freq_domain_notched[:] = freq_domain_corrected[:]
freq_domain_notched[bin_number] = 0 # Get rid of fundamental
freq_domain_notched[num_bins - bin_number] = 0 # and its negative
# Now just grab the fundamental
freq_domain_fund = np.zeros(num_bins)
freq_domain_fund[bin_number] = freq_domain_corrected[bin_number] # Grab the fundamental
freq_domain_fund[num_bins - bin_number] = freq_domain_corrected[num_bins - bin_number] # and its negative

extracted_dist = np.fft.ifft(freq_domain_notched) * num_bins
extracted_fund = np.fft.ifft(freq_domain_fund) * num_bins

# Now calculate the "primitive wave" of the extracted distortion. That is, pretend
# that the multiple cycles over the data record are actually a single cycle.
index = 0
extracted_primitive = np.zeros(num_bins)
points_per_cycle = num_bins / bin_number
for point in range(int(points_per_cycle)):
    for cycle in range(bin_number):
        extracted_primitive[index] = extracted_dist[int(cycle*points_per_cycle) + point]
        index +=1

#Now calculate a vector of an increasing half-cosine to use as the X axis...
cos_x_axis = np.zeros(num_bins)

y_axis = np.zeros(num_bins)
for t in range(num_bins):
    cos_x_axis[t] = 32768*np.cos(np.pi + np.pi*t/num_bins)
    y_axis[t] = extracted_primitive[int(num_bins/2 + t/2)]

x_axis = np.zeros(65536)
for code in range(65536):
    x_axis[code] = code-32768

# And finally... remap!!
# numpy.interp(x, xp, fp, left=None, right=None)[source]
lut_values = np.interp(x_axis, cos_x_axis, y_axis)
print("Some lut values:")
print(lut_values[-32000])
print(lut_values[0])
print(lut_values[32000])

dist_corr_waveform = np.zeros(num_bins)
for t in range (num_bins):
    dist_corr_waveform[t] = data[t] - lut_values[int(pure[t] * 32767/32768) - 32768]


plt.figure(1)
plt.subplot(2,1,1)
plt.title("Unshifted and shifted/corrected data")
plt.plot(data)
plt.plot(data_corrected)
plt.subplot(2,1,2)
plt.title("Shifted data")
plt.plot(data_shifted)
plt.show


plt.figure(2)
plt.subplot(2,1,1)
plt.title("extracted distortion")
#plt.plot(distortion)
plt.plot(extracted_dist)
plt.subplot(2,1,2)
plt.title("P-wave distortion")
plt.plot(extracted_primitive)
plt.show


plt.figure(3)
plt.subplot(3,1,1)
plt.title("cos weighted x axis")
#plt.plot(distortion)
plt.plot(cos_x_axis)
plt.subplot(3,1,2)
plt.title("distortion to map to weighted x axis")
plt.plot(y_axis)
plt.subplot(3,1,3)
plt.title("And finally... LUT values!")
plt.plot(lut_values)

plt.figure(4)
plt.title("Distorted data raw and with correction applied")
plt.plot(pure)
plt.plot(data)
plt.plot(dist_corr_waveform)
plt.show

# From http://earthseismology.blogspot.com/2010/11/time-shift-of-signal-using-fft-in.html
# TFshifted=TF.*exp(-i*w*2*pi*delay)
# NOTE that w*2*pi goes from zero to 1 cycles per sample!!

#function z=FFTshift(signal,delay,sample_Frequency);
#% Created by Piero Poli polipiero85@gmail.com
#
#X=signal; %signal to shift
#Fs=sample_Frequency; %sample frequency
#Xdelta=1/Fs;
#
#TF=fft(X);
#w=[0:floor((numel(X)-1)/2) -ceil((numel(X)-1)/2):-1]/(Xdelta*numel(X));
#
# TFshifted=TF.*exp(-i*w*2*pi*delay);
#n1=ceil(abs(delay)/Xdelta);
#Xs=real( ifft(TFshifted) );
#if delay <0
#OUTPUT_SIGNAL(1:numel(X)-n1)=Xs(1:numel(X)-n1);
#elseif delay>0
# OUTPUT_SIGNAL(n1:numel(X))=Xs(n1:numel(X));
#end
#
#z=OUTPUT_SIGNAL;